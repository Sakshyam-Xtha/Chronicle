from django.db import migrations, models

class Migration(migrations.Migration):

    # 1. Indicates if this is the first migration file for the app
    initial = True

    # 2. Lists other migration files that must run BEFORE this one
    dependencies = [
        
    ]

    # 3. Operations to be executed on the database
    operations = [
        migrations.AddField(
            model_name="user",
            name="age",
            field=models.IntegerField(),
        ),
    ]