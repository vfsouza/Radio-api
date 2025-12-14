from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import MultiPartParser, FormParser
import base64
import io


class YOLODetectionView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        try:
            image_file = request.FILES.get('image')
            additional_data = request.data.get('data', {})

            if not image_file:
                return Response(
                    {'error': 'No image provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            image_bytes = image_file.read()

            try:
                detections = self.process_with_yolo(image_bytes, additional_data)

                return Response({
                    'success': True,
                    'detections': detections,
                    'image_name': image_file.name,
                    'image_size': len(image_bytes),
                    'additional_data': additional_data
                }, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({
                    'error': f'YOLO processing error: {str(e)}',
                    'message': 'Make sure ultralytics is installed: pip install ultralytics'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def process_with_yolo(self, image_bytes, additional_data):
        try:
            from ultralytics import YOLO
            from PIL import Image

            image = Image.open(io.BytesIO(image_bytes))

            model = YOLO(r'../last.pt')

            results = model(image)

            detections = []
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    detection = {
                        'class': int(box.cls[0]),
                        'class_name': result.names[int(box.cls[0])],
                        'confidence': float(box.conf[0]),
                        'bbox': box.xyxy[0].tolist()
                    }
                    detections.append(detection)

            return detections

        except ImportError:
            return [{
                'message': 'YOLO not installed',
                'note': 'Install with: pip install ultralytics',
                'mock_detection': True,
                'class_name': 'example',
                'confidence': 0.95,
                'bbox': [100, 100, 200, 200]
            }]


class ImageUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        image_file = request.FILES.get('image')
        description = request.data.get('description', '')
        tags = request.data.get('tags', '')

        if not image_file:
            return Response(
                {'error': 'No image provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        response_data = {
            'success': True,
            'message': 'Image received successfully',
            'image_name': image_file.name,
            'image_size': image_file.size,
            'content_type': image_file.content_type,
            'description': description,
            'tags': tags
        }

        return Response(response_data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def health_check(request):
    yolo_available = False
    try:
        import ultralytics
        yolo_available = True
    except ImportError:
        pass

    return Response({
        'status': 'healthy',
        'message': 'API is running',
        'yolo_available': yolo_available
    }, status=status.HTTP_200_OK)
