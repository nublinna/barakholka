from django.core.management.base import BaseCommand
from ads.models import SiteStatistics

class Command(BaseCommand):
    help = 'Обновляет статистику сайта'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Показывать подробную информацию',
        )

    def handle(self, *args, **options):
        verbose = options['verbose']

        self.stdout.write('Обновление статистики сайта...')

        try:
            stats = SiteStatistics.get_current_stats()
            stats.update_stats()

            if verbose:
                self.stdout.write(self.style.SUCCESS('Статистика успешно обновлена:'))
                self.stdout.write(f'  Объявлений: {stats.total_ads}')
                self.stdout.write(f'  Активных объявлений: {stats.active_ads}')
                self.stdout.write(f'  Пользователей: {stats.total_users}')
                self.stdout.write(f'  Чатов: {stats.total_chats}')
                self.stdout.write(f'  Сообщений: {stats.total_messages}')
                self.stdout.write(f'  В избранном: {stats.total_favorites}')
            else:
                self.stdout.write(self.style.SUCCESS('Статистика успешно обновлена'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при обновлении статистики: {e}'))
