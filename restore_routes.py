import os
import re

with open('app/routes.py', 'r', encoding='utf-8') as f:
    content = f.read()

ai_logic = """
# =============================================================================
# RESTORED AI ANALYSIS & FUSION LOGIC
# =============================================================================
import json
import base64
import logging
from io import BytesIO
import typing
from datetime import datetime

try:
    import torch  # type: ignore
    import torch.nn as nn  # type: ignore
    from torchvision import models, transforms  # type: ignore
    TORCH_AVAILABLE = True
except Exception:
    class DummyModule:
        def __getattr__(self, name: str) -> typing.Any: return None
        def __call__(self, *args: typing.Any, **kwargs: typing.Any) -> typing.Any: return None
    torch = typing.cast(typing.Any, DummyModule())
    nn = typing.cast(typing.Any, DummyModule())
    models = typing.cast(typing.Any, DummyModule())
    transforms = typing.cast(typing.Any, DummyModule())
    TORCH_AVAILABLE = False


_skin_model = None
_skin_model_metadata: typing.Dict[str, typing.Any] = {}
_skin_model_labels = ['Oily', 'Dry', 'Normal', 'Acne']


def build_skin_classifier(architecture, num_classes):
    architecture = (architecture or 'efficientnet_v2_s').lower()
    
    if architecture == 'mobilenet_v3_large':
        model = models.mobilenet_v3_large(weights=None)
        in_features = model.classifier[-1].in_features
        model.classifier[-1] = nn.Sequential(
            nn.Linear(in_features, 256),
            nn.Hardswish(),
            nn.Dropout(0.2),
            nn.Linear(256, num_classes),
        ) # type: ignore
        return model

    if architecture == 'mobilenet_v2':
        model = models.mobilenet_v2(weights=None)
        model.classifier[1] = nn.Sequential(
            nn.Linear(model.last_channel, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, num_classes),
        ) # type: ignore
        return model

    model = models.efficientnet_v2_s(weights=None)
    in_features = model.classifier[-1].in_features
    model.classifier[-1] = nn.Sequential(
        nn.Linear(in_features, 256),
        nn.SiLU(),
        nn.Dropout(0.25),
        nn.Linear(256, num_classes),
    ) # type: ignore
    return model


def load_skin_model():
    global _skin_model
    if not TORCH_AVAILABLE:
        return None
    if _skin_model is not None:
        return _skin_model

    model_path = os.path.join(os.path.dirname(__file__), 'static', 'models', 'skin_classifier.pth')
    if not os.path.exists(model_path):
        return None
        
    try:
        device = torch.device('cpu')
        checkpoint = torch.load(model_path, map_location=device)
        arch = checkpoint.get('architecture', 'efficientnet_v2_s')
        labels = checkpoint.get('class_names', _skin_model_labels)
        
        model = build_skin_classifier(arch, len(labels))
        model.load_state_dict(checkpoint['model_state_dict']) # type: ignore
        model.eval() # type: ignore
        
        _skin_model = model
        _skin_model_metadata['labels'] = labels
        _skin_model_metadata['image_size'] = checkpoint.get('image_size', 224)
        return _skin_model
    except Exception as e:
        logging.error(f'Failed to load skin model: {e}')
        return None


def get_skin_preprocess():
    if not TORCH_AVAILABLE:
        return typing.cast(typing.Any, lambda x: x)
    size = _skin_model_metadata.get('image_size', 224)
    return transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(size),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])


def measure_image_quality(img):
    # Returns brightness, contrast, usable flag
    if not PIL_AVAILABLE:
        return {'brightness': 0.5, 'contrast': 0.5, 'usable': True}
    
    gray = img.convert('L')
    histogram = gray.histogram()
    total_pixels = sum(histogram)
    mean = sum(index * count for index, count in enumerate(histogram)) / total_pixels
    variance = sum(((index - mean) ** 2) * count for index, count in enumerate(histogram)) / total_pixels
    
    quality: typing.Dict[str, typing.Any] = {
        'brightness': float(f"{(mean / 255.0):.4f}"),
        'contrast': float(f"{((variance ** 0.5) / 255.0):.4f}"),
    }
    quality['usable'] = quality['brightness'] >= 0.22 and quality['contrast'] >= 0.12
    return quality


def average_region(img, x1, y1, x2, y2):
    region = img.crop((x1, y1, x2, y2))
    stat = region.getextrema()
    avg = [0.0, 0.0, 0.0]
    total = (x2 - x1) * (y2 - y1)
    try:
        r, g, b = region.split()
        avg[0] = sum(r.getdata()) / total
        avg[1] = sum(g.getdata()) / total
        avg[2] = sum(b.getdata()) / total
    except Exception:
        pass
    return avg


def score_visual_skin_cues(face_image):
    if not hasattr(face_image, 'crop'):
        return {'Oily': 0.25, 'Dry': 0.25, 'Normal': 0.25, 'Acne': 0.25}
        
    width, height = face_image.size
    t_zone = average_region(face_image, int(width * 0.32), int(height * 0.18), int(width * 0.68), int(height * 0.62))
    left_cheek = average_region(face_image, int(width * 0.12), int(height * 0.34), int(width * 0.30), int(height * 0.72))
    right_cheek = average_region(face_image, int(width * 0.70), int(height * 0.34), int(width * 0.88), int(height * 0.72))
    
    cheeks = (
        float((left_cheek[0] + right_cheek[0]) / 2.0),
        float((left_cheek[1] + right_cheek[1]) / 2.0),
        float((left_cheek[2] + right_cheek[2]) / 2.0)
    )
    
    t_zone_luma = (0.299 * t_zone[0]) + (0.587 * t_zone[1]) + (0.114 * t_zone[2])
    cheek_luma = (0.299 * cheeks[0]) + (0.587 * cheeks[1]) + (0.114 * cheeks[2])
    
    c0, c1, c2 = cheeks
    redness = max(0.0, float(((c0 - c1) + (c0 - c2)) / 255.0))
    oil_shift = max(0.0, float((t_zone_luma - cheek_luma) / 255.0))
    dryness_shift = max(0.0, float((cheek_luma - t_zone_luma) / 255.0))
    
    scores = {
        'Oily': 0.1 + min(0.6, oil_shift * 2.0),
        'Dry': 0.1 + min(0.6, dryness_shift * 1.5),
        'Normal': 0.4 - min(0.3, oil_shift + dryness_shift),
        'Acne': 0.1 + min(0.7, redness * 3.0)
    }
    
    total = sum(scores.values())
    if total > 0:
        return {k: v / total for k, v in scores.items()}
    return {'Oily': 0.25, 'Dry': 0.25, 'Normal': 0.25, 'Acne': 0.25}


def predict_skin_condition(image_bytes):
    model = load_skin_model()
    if not model or not TORCH_AVAILABLE or not PIL_AVAILABLE:
        return {
            'available': False,
            'label': None,
            'confidence': 0.0,
            'scores': {},
            'visual_scores': {},
            'quality': {},
            'error': 'AI components not loaded',
        }
        
    try:
        face_image = Image.open(BytesIO(image_bytes)).convert('RGB')
        quality = measure_image_quality(face_image)
        
        preprocess = get_skin_preprocess()
        input_tensor = preprocess(face_image).unsqueeze(0)
        
        with torch.no_grad():
            output = model(input_tensor)
            probabilities = torch.nn.functional.softmax(output[0], dim=0).tolist()
            
        labels = _skin_model_metadata.get('labels', _skin_model_labels)
        scores = {label: prob for label, prob in zip(labels, probabilities)}
        
        visual_scores = score_visual_skin_cues(face_image)
        label = str(max(scores.keys(), key=lambda k: float(scores.get(k, 0.0))))
        
        return {
            'available': True,
            'label': label,
            'confidence': scores[label],
            'scores': scores,
            'visual_scores': visual_scores,
            'quality': quality,
            'error': None,
        }
    except Exception as e:
        return {
            'available': False,
            'error': str(e),
            'scores': {},
            'visual_scores': {},
            'quality': {},
        }


def decode_image_payload(payload):
    # support array '["data:image...","data:image..."]' or single string
    images = []
    if payload.startswith('['):
        try:
            arr = json.loads(payload)
            for item in arr:
                if ',' in item:
                    images.append(base64.b64decode(item.split(',', 1)[1]))
        except Exception:
            pass
    elif ',' in payload:
        images.append(base64.b64decode(payload.split(',', 1)[1]))
    return images


def merge_prediction_results(frame_predictions):
    valid_predictions = [p for p in frame_predictions if p.get('available') and not p.get('error')]
    if not valid_predictions:
        return {
            'available': False,
            'scores': {},
            'visual_scores': {},
            'quality': {},
            'error': 'No valid frames generated a prediction',
        }
        
    merged_scores = {}
    merged_visual = {}
    brightness_values = []
    contrast_values = []
    usable_frames = 0
    
    for prediction in valid_predictions:
        for label, val in prediction.get('scores', {}).items():
            merged_scores[label] = merged_scores.get(label, 0.0) + val
            
        for label, val in prediction.get('visual_scores', {}).items():
            merged_visual[label] = merged_visual.get(label, 0.0) + val
            
        quality = prediction.get('quality', {})
        brightness_values.append(quality.get('brightness', 0.0))
        contrast_values.append(quality.get('contrast', 0.0))
        if quality.get('usable'):
            usable_frames += 1
            
    count = float(len(valid_predictions))
    merged_scores = {k: v / count for k, v in merged_scores.items()}
    merged_visual = {k: v / count for k, v in merged_visual.items()}
    label = str(max(merged_scores.keys(), key=lambda k: float(merged_scores.get(k, 0.0))))
    
    return {
        'available': True,
        'scores': merged_scores,
        'visual_scores': merged_visual,
        'quality': {
            'brightness': sum(brightness_values) / max(len(brightness_values), 1),
            'contrast': sum(contrast_values) / max(len(contrast_values), 1),
            'usable': usable_frames >= max(1, len(valid_predictions) // 2),
            'usable_frames': usable_frames,
            'frame_count': len(valid_predictions),
        },
        'confidence': merged_scores[label],
        'label': label,
        'error': None,
    }


def score_skin_questionnaire(form_data):
    feel = form_data.get('q_skin_feel', '')
    breakouts = form_data.get('q_breakouts', '')
    sensitive = form_data.get('q_sensitive', '')
    
    scores = {'Oily': 0.0, 'Dry': 0.0, 'Normal': 0.0, 'Acne': 0.0}
    
    if 'Oily and shiny' in feel:
        scores['Oily'] += 1.0
    elif 'Tight and flaky' in feel:
        scores['Dry'] += 1.0
    elif 'Oily in T-zone' in feel:
        scores['Oily'] += 0.5
        scores['Dry'] += 0.5
        scores['Normal'] += 0.5
    else:
        scores['Normal'] += 1.0
        
    if 'Yes' in breakouts:
        scores['Acne'] += 1.0
        scores['Oily'] += 0.3
        
    if 'Yes' in sensitive:
        scores['Dry'] += 0.5
        
    total = sum(scores.values()) or 1.0
    return {k: v / total for k, v in scores.items()}


def blend_skin_scores(ai_scores, quiz_scores, visual_scores, ai_weight=0.5, visual_weight=0.3, quiz_weight=0.2):
    final_scores = {}
    labels = set(ai_scores.keys()) | set(quiz_scores.keys()) | set(visual_scores.keys())
    for label in labels:
        final_scores[label] = (
            ai_scores.get(label, 0.0) * ai_weight +
            visual_scores.get(label, 0.0) * visual_weight +
            quiz_scores.get(label, 0.0) * quiz_weight
        )
    return final_scores


def score_final_skin_labels(component_scores, quiz_scores, visual_scores, form_data):
    oily = component_scores.get('Oily', 0.0)
    dry = component_scores.get('Dry', 0.0)
    acne = component_scores.get('Acne', 0.0)
    normal = component_scores.get('Normal', 0.0)
    
    scores = {
        'Oily & Acne-Prone': oily * 0.6 + acne * 0.4,
        'Dry & Sensitive': dry * 0.7 + (0.3 if form_data.get('q_sensitive') == 'Yes' else 0.0),
        'Combination': (oily + dry) / 2.0,
        'Normal': normal
    }
    
    # Give combination a boost if feel explicitly stated it
    if 'Oily in T-zone' in form_data.get('q_skin_feel', ''):
        scores['Combination'] += 0.2
        
    total = sum(scores.values()) or 1.0
    return {k: v / total for k, v in scores.items()}


def get_skin_recommendations(findings):
    keywords = {
        'Oily & Acne-Prone': ['acne', 'acne prone', 'blemish', 'salicylic', 'oil free', 'non comedogenic'],
        'Dry & Sensitive': ['dry', 'hydration', 'moisture', 'barrier', 'sensitive', 'gentle'],
        'Combination': ['balanced', 'lightweight', 'gentle', 'hydration', 'oil control'],
        'Normal': ['normal', 'balanced', 'gentle', 'daily'],
    }.get(findings, [findings.lower()])

    filters = []
    for keyword in keywords:
        filters.append(Product.target_condition.ilike(f'%{keyword}%'))
        filters.append(Product.skin_type.ilike(f'%{keyword}%'))
        filters.append(Product.description.ilike(f'%{keyword}%'))
        filters.append(Product.name.ilike(f'%{keyword}%'))

    from sqlalchemy import or_
    recommendations = Product.query.filter_by(category='skin').filter(or_(*filters)).limit(4).all()
    if recommendations:
        return recommendations

    from sqlalchemy.sql.expression import func  # type: ignore
    return Product.query.filter_by(category='skin').order_by(func.random()).limit(4).all()


def save_uploaded_analysis_file(f):
    name = save_uploaded_image(f)
    if not name:
        return None, []
    path = os.path.join(_images_folder(), name)
    try:
        with open(path, 'rb') as f:
            data = f.read()
            return url_for('static', filename='images/' + name), [data]
    except Exception:
        return None, []


def save_analysis_capture(image_b64):
    images = decode_image_payload(image_b64 or '')
    if not images:
        return None, []
    
    name = uuid4().hex + '.jpg'
    path = os.path.join(_images_folder(), name)
    with open(path, 'wb') as f:
        f.write(images[0])
    return url_for('static', filename='images/' + name), images


@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    '''Skin-only AI analysis flow backed by the PyTorch scanner.'''
    recommendations = []
    image_url = None
    findings = None
    confidence = None
    quality_note = None
    model_available = load_skin_model() is not None
    scanner_mode = 'AI + quiz fusion' if model_available else 'Quiz-first fallback'

    if request.method == 'POST':
        image_b64 = request.form.get('image_base64')
        image_file = request.files.get('image_file')

        try:
            if image_file and getattr(image_file, 'filename', ''):
                image_url, captured_images = save_uploaded_analysis_file(image_file)
            else:
                image_url, captured_images = save_analysis_capture(image_b64)
        except Exception as exc:
            logging.error('Image save error: %s', exc)
            image_url, captured_images = None, []

        quiz_scores = score_skin_questionnaire(request.form)
        if captured_images:
            frame_predictions = [predict_skin_condition(image_bytes) for image_bytes in captured_images]
            ai_result = merge_prediction_results(frame_predictions)
        else:
            ai_result = {
                'available': False,
                'label': None,
                'confidence': 0.0,
                'scores': {},
                'visual_scores': {},
                'quality': {},
                'error': 'No image provided',
            }
        component_scores = blend_skin_scores(
            typing.cast(dict, ai_result.get('scores', {})),
            quiz_scores,
            typing.cast(dict, ai_result.get('visual_scores', {})),
            ai_weight=(0.5 if ai_result.get('quality', {}).get('usable') else 0.2)
        )
        final_scores = score_final_skin_labels(
            component_scores,
            quiz_scores,
            typing.cast(dict, ai_result.get('visual_scores', {})),
            request.form,
        )
        findings = str(max(final_scores.keys(), key=lambda k: float(final_scores.get(k, 0.0))))
        confidence = float(f"{(final_scores[findings] * 100):.1f}")
        model_available = ai_result.get('available', False)
        quality = ai_result.get('quality', {})
        quality_ok = quality.get('usable', False)
        if model_available and quality_ok:
            scanner_mode = 'AI + quiz fusion'
        elif model_available:
            scanner_mode = 'Quiz-led fusion due to low-quality scan'
        else:
            scanner_mode = 'Quiz-first fallback'

        if quality and not quality_ok:
            quality_note = 'Low-light or blurry capture detected, so the quiz was weighted more heavily than the scan.'
            confidence = float(f"{(confidence * 0.88):.1f}")

        if session.get('user_id'):
            user = db.session.get(User, session.get('user_id'))
            if user:
                user.detected_skin_type = findings
                db.session.commit()

        recommendations = get_skin_recommendations(findings)

    return render_template(
        'analyze.html', 
        recommendations=recommendations, 
        image_url=image_url, 
        findings=findings,
        confidence=confidence,
        scanner_mode=scanner_mode,
        quality_note=quality_note
    )

# =============================================================================
"""

# Replace the existing old 'analyze' function block entirely
pattern = r'# simple AI analysis helpers\s+.*?(?=@app\.route\(\'/payment/success\'\))'
new_content = re.sub(pattern, ai_logic, content, flags=re.DOTALL)

with open('app/routes.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

