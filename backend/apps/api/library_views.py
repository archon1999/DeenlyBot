from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.content.models import Dua, QuranPassage
from apps.content.study_services import passage_analysis
from apps.library_learning.models import UserLibraryProgress
from apps.library_learning.services import (
    answer_library_quiz,
    build_library_quiz,
    confirm_library_studied,
    library_progress_stats,
)

from . import dto
from .serializers import LibraryQuizInput, QuizAnswerInput
from .views import validated


class LibraryDetailView(APIView):
    def get(self, request, kind, item_id):
        if kind == "dua":
            item = Dua.objects.prefetch_related("translations").get(id=item_id, is_published=True)
            lookup = {"dua_id": item.id}
        elif kind in ("ayah", "surah"):
            item = QuranPassage.objects.prefetch_related("translations").get(
                id=item_id, passage_type=kind, is_published=True
            )
            lookup = {"passage_id": item.id}
        else:
            raise ValidationError({"kind": "Choose ayah, surah or dua"})
        studied = UserLibraryProgress.objects.filter(user=request.profile, **lookup).exists()
        result = dto.library_dto(
            item, kind, request.profile, studied_ids={item.id} if studied else set()
        )
        result["analysis"] = (
            passage_analysis(item, request.profile.language) if kind != "dua" else None
        )
        return Response(result)


class LibraryStudyView(APIView):
    def post(self, request, kind, item_id):
        _, created = confirm_library_studied(request.profile, kind, item_id)
        return Response({"created": created, "is_studied": True})


class LibraryPracticeView(APIView):
    def get(self, request):
        kind = request.query_params.get("kind", "ayah")
        return Response({"stats": library_progress_stats(request.profile, kind)})


class LibraryQuizView(APIView):
    def post(self, request):
        data = validated(LibraryQuizInput, request)
        question = build_library_quiz(request.profile, **data)
        return Response({"question": dto.quiz_dto(question)})


class LibraryQuizAnswerView(APIView):
    def post(self, request, question_id):
        data = validated(QuizAnswerInput, request)
        question, accepted = answer_library_quiz(
            question_id, request.profile, data["selected_option"]
        )
        return Response(
            {
                "accepted": accepted,
                "is_correct": question.is_correct,
                "correct_option": question.correct_option,
                "answer_label": question.options[question.correct_option]["label"],
                "answer_meaning": question.answer_translation,
            }
        )
