from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("content", "0002_duatranslation_transcription_and_more")]

    operations = [
        migrations.AlterModelOptions(
            name="dua",
            options={"ordering": ["id"]},
        ),
    ]
