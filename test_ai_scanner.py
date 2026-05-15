# pyre-ignore-all-errors
import base64
from io import BytesIO

from PIL import Image

from app import db
from models import Product


def make_base64_image(color=(210, 180, 170)):
    image = Image.new('RGB', (320, 420), color=color)
    buffer = BytesIO()
    image.save(buffer, format='JPEG')
    encoded = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f'data:image/jpeg;base64,{encoded}'


def test_final_skin_label_scoring_prefers_oily_acne_prone():
    from app import ai_bp

    quiz_scores = ai_bp.score_skin_questionnaire({
        'q_skin_feel': 'Oily and shiny',
        'q_breakouts': 'Yes',
        'q_sensitive': 'No',
    })
    component_scores = ai_bp.blend_skin_scores(
        ai_scores={'Oily': 0.44, 'Dry': 0.05, 'Normal': 0.07, 'Acne': 0.44},
        quiz_scores=quiz_scores,
        visual_scores={'Oily': 0.48, 'Dry': 0.08, 'Normal': 0.08, 'Acne': 0.36},
    )
    final_scores = ai_bp.score_final_skin_labels(
        component_scores,
        quiz_scores,
        {'Oily': 0.48, 'Dry': 0.08, 'Normal': 0.08, 'Acne': 0.36},
        {'q_skin_feel': 'Oily and shiny', 'q_breakouts': 'Yes', 'q_sensitive': 'No'},
    )

    assert max(final_scores, key=final_scores.get) == 'Oily & Acne-Prone'
    assert final_scores['Oily & Acne-Prone'] > final_scores['Dry & Sensitive']


def test_decode_image_payload_supports_burst_capture():
    from app import ai_bp

    single = make_base64_image()
    payload = f'["{single}","{single}"]'
    decoded = ai_bp.decode_image_payload(payload)

    assert len(decoded) == 2
    assert all(decoded)


def test_merge_prediction_results_averages_frames():
    from app import ai_bp

    merged = ai_bp.merge_prediction_results([
        {
            'available': True,
            'scores': {'Oily': 0.6, 'Dry': 0.1, 'Normal': 0.1, 'Acne': 0.2},
            'visual_scores': {'Oily': 0.5, 'Dry': 0.1, 'Normal': 0.2, 'Acne': 0.2},
            'quality': {'brightness': 0.4, 'contrast': 0.2, 'usable': True},
        },
        {
            'available': True,
            'scores': {'Oily': 0.4, 'Dry': 0.2, 'Normal': 0.2, 'Acne': 0.2},
            'visual_scores': {'Oily': 0.4, 'Dry': 0.2, 'Normal': 0.2, 'Acne': 0.2},
            'quality': {'brightness': 0.3, 'contrast': 0.18, 'usable': True},
        },
    ])

    assert merged['available'] is True
    assert merged['quality']['usable'] is True
    assert round(merged['scores']['Oily'], 2) == 0.50


def test_combination_path_uses_quiz_and_visual_balance():
    from app import ai_bp

    quiz_scores = ai_bp.score_skin_questionnaire({
        'q_skin_feel': 'Oily in T-zone, dry elsewhere',
        'q_breakouts': 'No',
        'q_sensitive': 'No',
    })
    component_scores = ai_bp.blend_skin_scores(
        ai_scores={'Oily': 0.31, 'Dry': 0.24, 'Normal': 0.33, 'Acne': 0.12},
        quiz_scores=quiz_scores,
        visual_scores={'Oily': 0.38, 'Dry': 0.24, 'Normal': 0.28, 'Acne': 0.10},
    )
    final_scores = ai_bp.score_final_skin_labels(
        component_scores,
        quiz_scores,
        {'Oily': 0.38, 'Dry': 0.24, 'Normal': 0.28, 'Acne': 0.10},
        {'q_skin_feel': 'Oily in T-zone, dry elsewhere', 'q_breakouts': 'No', 'q_sensitive': 'No'},
    )

    assert max(final_scores, key=final_scores.get) == 'Combination'


def test_analyze_and_home_pages_keep_skin_quiz_flow(client):
    analyze_response = client.get('/analyze')
    analyze_html = analyze_response.get_data(as_text=True)
    assert analyze_response.status_code == 200
    assert "Discover Your Skin's Needs" in analyze_html
    assert 'Hair Analysis' not in analyze_html

    home_response = client.get('/')
    home_html = home_response.get_data(as_text=True)
    assert home_response.status_code == 200
    assert 'Next-Gen AI Diagnostics' in home_html
    assert 'hair concerns' not in home_html


def test_skin_scanner_recommends_oily_acne_products(client, monkeypatch):
    from app import ai_bp

    with client.application.app_context():
        db.session.add_all([
            Product(
                name='Salicylic Acid Cleanser',
                category='skin',
                price=399.0,
                description='Oil-control cleanser for acne-prone skin',
                skin_type='Oily',
                target_condition='Acne',
            ),
            Product(
                name='Barrier Cream',
                category='skin',
                price=499.0,
                description='Moisturizer for dry skin',
                skin_type='Dry',
                target_condition='Dry',
            ),
        ])
        db.session.commit()

    monkeypatch.setattr(
        ai_bp,
        'predict_skin_condition',
        lambda image_bytes: {
            'available': True,
            'label': 'Acne',
            'confidence': 0.82,
            'scores': {
                'Oily': 0.34,
                'Dry': 0.03,
                'Normal': 0.05,
                'Acne': 0.58,
            },
            'visual_scores': {
                'Oily': 0.46,
                'Dry': 0.08,
                'Normal': 0.10,
                'Acne': 0.36,
            },
            'error': None,
        },
    )

    response = client.post('/analyze', data={
        'csrf_token': 'test-token',
        'q_skin_feel': 'Oily and shiny',
        'q_breakouts': 'Yes',
        'q_sensitive': 'No',
        'image_base64': make_base64_image(),
    })
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'Oily &amp; Acne-Prone' in html or 'Oily & Acne-Prone' in html
    assert 'Salicylic Acid Cleanser' in html


def test_upload_photo_path_works_for_analysis(client, monkeypatch):
    from app import ai_bp

    monkeypatch.setattr(
        ai_bp,
        'predict_skin_condition',
        lambda image_bytes: {
            'available': True,
            'label': 'Acne',
            'confidence': 0.8,
            'scores': {
                'Oily': 0.32,
                'Dry': 0.05,
                'Normal': 0.08,
                'Acne': 0.55,
            },
            'visual_scores': {
                'Oily': 0.40,
                'Dry': 0.10,
                'Normal': 0.10,
                'Acne': 0.40,
            },
            'quality': {'brightness': 0.4, 'contrast': 0.2, 'usable': True},
            'error': None,
        },
    )

    image = Image.new('RGB', (320, 420), color=(215, 180, 180))
    file_buffer = BytesIO()
    image.save(file_buffer, format='JPEG')
    file_buffer.seek(0)

    response = client.post('/analyze', data={
        'csrf_token': 'test-token',
        'q_skin_feel': 'Oily and shiny',
        'q_breakouts': 'Yes',
        'q_sensitive': 'No',
        'image_file': (file_buffer, 'acne-face.jpg'),
    }, content_type='multipart/form-data')

    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert 'Oily &amp; Acne-Prone' in html or 'Oily & Acne-Prone' in html
