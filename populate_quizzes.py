# Exportar variável de ambiente: $env:DJANGO_SETTINGS_MODULE="SEA.settings"
# Execute: python manage.py shell < populate_quizzes.py
# ou: python populate_quizzes.py

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SEA.settings')
django.setup()

from core.models import Quiz

# Limpa quizzes existentes
Quiz.objects.all().delete()

# Cria os 3 desafios
quizzes_data = [
    {
        'numero': 1,
        'titulo': 'Olhômetro Calibrado',
        'subtítulo': 'Sem régua, sem paquímetro, sem choro...',
        'descricao': 'Sem régua, sem paquímetro, sem choro...',
        'icone': 'bi-rulers',
        'pergunta': 'Qual é a distância do canal indicado na peça?',
        'unidade_medida': 'mm',
        'valor_minimo': 118.09,
        'valor_maximo': 227.61,
        'dica': 'Observe cuidadosamente a escala da imagem. A distância está entre 100 e 250mm.'
    },
    {
        'numero': 2,
        'titulo': 'Mistério dos Cavacos',
        'subtítulo': 'Se não tem cavaco, não tem história...',
        'descricao': 'Uma caixa de cavaco misteriosa apareceu. Ninguém viu nada. Todo mundo tem um palpite...',
        'icone': 'bi-box-seam',
        'pergunta': 'Estime a massa da caixa com cavacos:',
        'unidade_medida': 'gramas',
        'valor_minimo': 1035,
        'valor_maximo': 4590,
        'dica': 'Considere o volume aparente da caixa e a densidade dos cavacos de usinagem.'
    },
    {
        'numero': 3,
        'titulo': 'CSI Jaraguá: Matador de Ferramenta!',
        'subtítulo': 'A caixa parece uma cena de crime: quebras, lascamentos, superaquecimento...',
        'descricao': 'A caixa parece uma cena de crime: quebras, lascamentos, superaquecimento. Você é o perito.',
        'icone': 'bi-search',
        'pergunta': 'Quantas unidades (inteiras ou não) de ferramentas estão na caixa?',
        'unidade_medida': 'unidades',
        'valor_minimo': 40,
        'valor_maximo': 183,
        'dica': 'Conte cuidadosamente todas as ferramentas, incluindo as quebradas e fragmentos significativos.'
    }
]

for quiz_data in quizzes_data:
    Quiz.objects.create(**quiz_data)
    print(f"✓ Quiz {quiz_data['numero']} criado com sucesso!")

print(f"\nTotal de quizzes criados: {Quiz.objects.count()}")