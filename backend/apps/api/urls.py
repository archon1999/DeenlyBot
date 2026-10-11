from django.urls import path

from . import account_views, library_views, views

app_name = "api"

urlpatterns = [
    path("auth/guest/", account_views.GuestView.as_view()),
    path("auth/register/", account_views.RegisterView.as_view()),
    path("auth/login/", account_views.LoginView.as_view()),
    path("auth/profile/", account_views.ProfileView.as_view()),
    path("auth/telegram/link/start/", account_views.TelegramLinkStartView.as_view()),
    path("auth/telegram/link/complete/", account_views.TelegramLinkCompleteView.as_view()),
    path("auth/session/", views.SessionView.as_view(), name="session"),
    path("auth/telegram/start/", views.TelegramLoginStartView.as_view()),
    path("auth/telegram/complete/", views.TelegramLoginCompleteView.as_view()),
    path("auth/miniapp/", views.MiniAppLoginView.as_view()),
    path("auth/logout/", views.LogoutView.as_view()),
    path("dashboard/", views.DashboardView.as_view()),
    path("names/", views.NamesView.as_view()),
    path("names/<int:name_id>/confirm/", views.NameConfirmView.as_view()),
    path("names/quiz/", views.NameQuizView.as_view()),
    path("names/quiz/<uuid:question_id>/answer/", views.NameQuizAnswerView.as_view()),
    path("arabic/", views.ArabicView.as_view()),
    path("arabic/lessons/<int:lesson_id>/", views.ArabicLessonView.as_view()),
    path(
        "arabic/lessons/<int:lesson_id>/start/",
        views.ArabicLessonActionView.as_view(),
        {"action": "start"},
    ),
    path(
        "arabic/lessons/<int:lesson_id>/complete/",
        views.ArabicLessonActionView.as_view(),
        {"action": "complete"},
    ),
    path("arabic/quiz/", views.ArabicQuizView.as_view()),
    path("arabic/quiz/<uuid:question_id>/answer/", views.ArabicQuizAnswerView.as_view()),
    path("library/", views.LibraryView.as_view()),
    path("library/practice/", library_views.LibraryPracticeView.as_view()),
    path("library/quiz/", library_views.LibraryQuizView.as_view()),
    path("library/quiz/<uuid:question_id>/answer/", library_views.LibraryQuizAnswerView.as_view()),
    path("library/<str:kind>/<int:item_id>/", library_views.LibraryDetailView.as_view()),
    path("library/<str:kind>/<int:item_id>/study/", library_views.LibraryStudyView.as_view()),
    path("library/<str:kind>/<int:item_id>/favorite/", views.FavoriteView.as_view()),
    path("qada/", views.QadaView.as_view()),
    path("qada/configure/", views.QadaConfigureView.as_view()),
    path("qada/add/", views.QadaAddView.as_view()),
    path("qada/complete/", views.QadaCompleteView.as_view()),
    path("qada/fast/", views.FastView.as_view()),
    path("calendar/", views.CalendarView.as_view()),
    path("reports/", views.ReportsView.as_view()),
    path("settings/", views.SettingsView.as_view()),
]
