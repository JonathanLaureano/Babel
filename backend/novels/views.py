from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Novel, Chapter
from .serializers import NovelSerializer, NovelListSerializer, ChapterSerializer


class NovelViewSet(viewsets.ModelViewSet):
    queryset = Novel.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return NovelListSerializer
        return NovelSerializer
    
    @action(detail=True, methods=['get'])
    def chapters(self, request, pk=None):
        novel = self.get_object()
        chapters = novel.chapters.all()
        serializer = ChapterSerializer(chapters, many=True)
        return Response(serializer.data)


class ChapterViewSet(viewsets.ModelViewSet):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer
    
    def get_queryset(self):
        queryset = Chapter.objects.all()
        novel_id = self.request.query_params.get('novel', None)
        if novel_id is not None:
            queryset = queryset.filter(novel_id=novel_id)
        return queryset

