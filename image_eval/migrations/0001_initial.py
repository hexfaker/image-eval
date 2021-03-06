# Generated by Django 2.2.dev20181219114131 on 2018-12-19 21:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Evaluation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField()),
                ('type', models.CharField(choices=[('SEL', 'Image selection'), ('CLS', 'Image classification')], max_length=10)),
                ('total_questions', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=1000)),
                ('order', models.IntegerField()),
                ('evaluation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='image_eval.Evaluation')),
            ],
        ),
        migrations.CreateModel(
            name='ImageClassificationQuestion',
            fields=[
                ('question_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='image_eval.Question')),
                ('image', models.ImageField(upload_to='')),
                ('answers', models.TextField()),
            ],
            bases=('image_eval.question',),
        ),
        migrations.CreateModel(
            name='ImageSelectionQuestion',
            fields=[
                ('question_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='image_eval.Question')),
                ('left_image', models.ImageField(upload_to='')),
                ('right_image', models.ImageField(upload_to='')),
            ],
            bases=('image_eval.question',),
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hash', models.CharField(max_length=32, unique=True)),
                ('user_name', models.CharField(max_length=100)),
                ('comment', models.CharField(max_length=10000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(null=True)),
                ('evaluation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='image_eval.Evaluation')),
            ],
        ),
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.IntegerField()),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='image_eval.Question')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='image_eval.Session')),
            ],
        ),
    ]
