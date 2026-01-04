"""
Django management command to load and manage the RAG knowledge base.

Usage:
    python manage.py load_knowledge --all           # Load all knowledge bases
    python manage.py load_knowledge --agent legal   # Load specific agent's knowledge
    python manage.py load_knowledge --status        # Check knowledge base status
    python manage.py load_knowledge --locations     # Show upload file locations
"""

from django.core.management.base import BaseCommand, CommandError
from analyzer.rag_system import (
    initialize_knowledge_base,
    load_agent_knowledge,
    get_knowledge_base_status,
    get_upload_locations,
    refresh_knowledge_base,
)


class Command(BaseCommand):
    help = 'Load and manage RAG knowledge base for India-focused startup analysis'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Load all knowledge bases (legal, market, costs)',
        )
        parser.add_argument(
            '--agent',
            type=str,
            choices=['legal', 'market', 'costs'],
            help='Load knowledge base for a specific agent',
        )
        parser.add_argument(
            '--status',
            action='store_true',
            help='Show current status of all knowledge bases',
        )
        parser.add_argument(
            '--locations',
            action='store_true',
            help='Show file upload locations for each agent',
        )
        parser.add_argument(
            '--refresh',
            action='store_true',
            help='Refresh/reload knowledge bases',
        )

    def handle(self, *args, **options):
        if options['locations']:
            self._show_locations()
        elif options['status']:
            self._show_status()
        elif options['all'] or options['refresh']:
            self._load_all()
        elif options['agent']:
            self._load_agent(options['agent'])
        else:
            self.stdout.write(self.style.WARNING(
                'No action specified. Use --help to see available options.'
            ))
            self._show_status()

    def _load_all(self):
        """Load all knowledge bases."""
        self.stdout.write(self.style.HTTP_INFO('Loading all knowledge bases...'))
        self.stdout.write('')
        
        try:
            results = initialize_knowledge_base()
            
            total = 0
            for agent, count in results.items():
                if count > 0:
                    self.stdout.write(self.style.SUCCESS(
                        f'  ✓ {agent.upper()}: Loaded {count} chunks'
                    ))
                else:
                    self.stdout.write(self.style.WARNING(
                        f'  ⚠ {agent.upper()}: No documents found'
                    ))
                total += count
            
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS(
                f'Knowledge base loaded successfully! Total: {total} chunks'
            ))
            
        except Exception as e:
            raise CommandError(f'Failed to load knowledge base: {e}')

    def _load_agent(self, agent_type: str):
        """Load knowledge base for a specific agent."""
        self.stdout.write(self.style.HTTP_INFO(
            f'Loading {agent_type.upper()} knowledge base...'
        ))
        
        try:
            count = load_agent_knowledge(agent_type)
            
            if count > 0:
                self.stdout.write(self.style.SUCCESS(
                    f'Successfully loaded {count} chunks for {agent_type.upper()} agent'
                ))
            else:
                self.stdout.write(self.style.WARNING(
                    f'No documents found for {agent_type.upper()} agent'
                ))
                locations = get_upload_locations()
                self.stdout.write(self.style.WARNING(
                    f'Upload documents to: {locations[agent_type]["path"]}'
                ))
                
        except Exception as e:
            raise CommandError(f'Failed to load {agent_type} knowledge: {e}')

    def _show_status(self):
        """Show knowledge base status."""
        self.stdout.write(self.style.HTTP_INFO('Knowledge Base Status:'))
        self.stdout.write('')
        
        try:
            status = get_knowledge_base_status()
            
            for agent, info in status.items():
                chunks = info.get('chunks', 0)
                directory = info.get('directory', 'Unknown')
                error = info.get('error')
                
                if error:
                    self.stdout.write(self.style.ERROR(
                        f'  ✗ {agent.upper()}: Error - {error}'
                    ))
                elif chunks > 0:
                    self.stdout.write(self.style.SUCCESS(
                        f'  ✓ {agent.upper()}: {chunks} chunks loaded'
                    ))
                else:
                    self.stdout.write(self.style.WARNING(
                        f'  ○ {agent.upper()}: No data (upload files to {directory})'
                    ))
            
            self.stdout.write('')
            
        except Exception as e:
            raise CommandError(f'Failed to get status: {e}')

    def _show_locations(self):
        """Show file upload locations."""
        self.stdout.write(self.style.HTTP_INFO('File Upload Locations:'))
        self.stdout.write('')
        
        locations = get_upload_locations()
        
        for agent, info in locations.items():
            self.stdout.write(self.style.SUCCESS(f'  {agent.upper()} Agent:'))
            self.stdout.write(f'    Path: {info["path"]}')
            self.stdout.write(f'    Description: {info["description"]}')
            self.stdout.write(f'    Supported formats: {", ".join(info["supported_formats"])}')
            self.stdout.write(f'    Example files:')
            for example in info["example_files"]:
                self.stdout.write(f'      - {example}')
            self.stdout.write('')
        
        self.stdout.write(self.style.HTTP_INFO(
            'After adding files, run: python manage.py load_knowledge --all'
        ))
