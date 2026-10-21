"""
Conteúdo educativo das páginas de dicas (abertas pelos cards da página inicial).

São dicas GERAIS de bem-estar: sem calorias, sem quantidades de alimentos
e sem orientação individual. Cada tema tem a sua cor (chave de
styles.CORES_CARDS_INICIO) e termina com um aviso de que não substitui
a orientação profissional.

Para editar um texto, basta mudar as frases abaixo; a página se monta sozinha.
"""

AVISO = (
    "Estas são dicas gerais e educativas. Elas não substituem a orientação "
    "da sua nutricionista nem de outros profissionais de saúde."
)

# Ordem em que os temas aparecem na página inicial e no menu das dicas.
TEMAS = {
    "sono": {
        "cor": "rosa",
        "icone": "🌙",
        "titulo": "Sono e rotina",
        "resumo": "Higiene do sono e uma rotina noturna que ajuda a descansar melhor.",
        "introducao": (
            "Dormir bem é a base da energia, do humor e da concentração. "
            "Pequenos hábitos repetidos todos os dias fazem muita diferença."
        ),
        "secoes": [
            ("🛏️", "Higiene do sono", [
                "Tente dormir e acordar sempre nos mesmos horários, inclusive nos fins de semana.",
                "Deixe o quarto escuro, silencioso e com temperatura agradável.",
                "Use a cama para dormir: evite trabalhar, comer ou ficar no celular deitado.",
                "Se cochilar durante o dia, prefira cochilos curtos e no começo da tarde.",
            ]),
            ("🌙", "Rotina antes de dormir", [
                "Reserve um tempo para desacelerar antes de deitar: diminua as luzes da casa.",
                "Deixe o celular e outras telas de lado e, se possível, fora do quarto.",
                "Um banho morno, uma leitura leve ou alongamentos suaves ajudam o corpo a relaxar.",
                "Se a cabeça estiver cheia, anote as preocupações e as tarefas do dia seguinte.",
                "Experimente respirar devagar, soltando o ar mais lentamente do que puxou.",
            ]),
            ("☕", "O que pode atrapalhar", [
                "Café, chá preto, chá-mate, refrigerantes de cola e energéticos à tarde e à noite.",
                "Bebidas alcoólicas: podem dar sono, mas pioram a qualidade do descanso.",
                "Refeições muito pesadas ou gordurosas perto da hora de dormir.",
                "Exercícios muito intensos logo antes de deitar.",
            ]),
            ("☀️", "Ao acordar", [
                "Abra as janelas e receba luz natural logo cedo: isso ajusta o relógio do corpo.",
                "Levante no mesmo horário todos os dias, mesmo depois de uma noite ruim.",
                "Se a insônia, o ronco forte ou o cansaço forem frequentes, procure um profissional de saúde.",
            ]),
        ],
    },
    "energia": {
        "cor": "amarelo",
        "icone": "⚡",
        "titulo": "Energia no dia a dia",
        "resumo": "Pausas, hidratação e luz do dia para manter a disposição.",
        "introducao": (
            "Sentir cansaço no meio do dia é comum, mas alguns hábitos simples "
            "ajudam a manter a disposição de forma mais estável."
        ),
        "secoes": [
            ("⏸️", "Faça pausas", [
                "Intercale períodos de concentração com pequenas pausas para levantar e se movimentar.",
                "Nas pausas, alongue o pescoço, os ombros e as costas.",
                "Descanse os olhos olhando para longe da tela de vez em quando.",
                "Organize as tarefas mais difíceis para o período em que você costuma ter mais energia.",
            ]),
            ("💧", "Hidratação", [
                "Às vezes o cansaço e a dor de cabeça são sinais de que falta água.",
                "Deixe uma garrafinha de água por perto e beba ao longo do dia, sem esperar a sede.",
                "Frutas como melancia, laranja e abacaxi também ajudam a hidratar.",
                "Prefira água a refrigerantes e sucos industrializados.",
            ]),
            ("☀️", "Luz do dia", [
                "Receba luz natural pela manhã: abra janelas ou dê uma volta ao ar livre.",
                "Se puder, trabalhe ou estude perto de uma janela.",
                "Uma caminhada curta ao ar livre depois do almoço ajuda a espantar o sono.",
                "Ao tomar sol, lembre-se do protetor solar e evite os horários de sol mais forte.",
            ]),
            ("🍎", "Alimentação e disposição", [
                "Mantenha refeições em horários regulares e evite passar longos períodos sem comer.",
                "Prefira alimentos integrais, frutas e verduras aos doces, que dão energia rápida e depois cansaço.",
                "Café pode ajudar pela manhã, mas evite exagerar e deixe-o de lado no fim do dia.",
            ]),
            ("🧘", "Cuide da mente", [
                "Respirar fundo por alguns instantes ajuda a baixar o estresse.",
                "Conversar com alguém, ouvir uma música ou dar uma risada também renova a energia.",
                "Dormir bem é a principal fonte de energia: veja também as dicas de sono.",
            ]),
        ],
    },
    "alimentacao": {
        "cor": "verde_agua",
        "icone": "🥗",
        "titulo": "Alimentação",
        "resumo": "Alimentos para cada período do dia, hidratação e lanches saudáveis.",
        "introducao": (
            "Comer bem não precisa ser complicado. A base é \"comida de verdade\": "
            "alimentos frescos ou pouco processados, refeições coloridas e momentos "
            "de comer com calma."
        ),
        "secoes": [
            ("🌅", "Manhã", [
                "Frutas da estação, inteiras ou picadas.",
                "Alimentos integrais, como aveia, pão integral, tapioca com recheio ou cuscuz.",
                "Uma fonte de proteína, como ovos, iogurte natural ou queijo branco.",
                "Café, se gostar, de preferência sem muito açúcar.",
            ]),
            ("☀️", "Almoço", [
                "Monte um prato colorido: verduras, legumes, arroz (de preferência integral) ou tubérculos.",
                "Inclua feijão, lentilha, grão-de-bico ou ervilha.",
                "Escolha uma fonte de proteína, como carnes magras, frango, peixe ou ovos.",
                "Coma devagar e, se puder, longe das telas.",
            ]),
            ("🌇", "Tarde", [
                "Um lanche ajuda a não chegar com muita fome ao jantar.",
                "Boas opções: fruta, iogurte natural, castanhas ou pão integral com pasta de grão-de-bico.",
            ]),
            ("🌙", "Noite", [
                "Prefira refeições mais leves, como sopas, legumes, omeletes ou saladas completas.",
                "Evite frituras, muito açúcar e refeições pesadas perto da hora de dormir.",
                "Chás de ervas sem cafeína, como camomila e erva-cidreira, são boas opções.",
            ]),
            ("💧", "Hidratação", [
                "Beba água ao longo do dia; deixar uma garrafinha por perto ajuda a lembrar.",
                "Xixi claro costuma ser sinal de boa hidratação.",
                "Em dias quentes e quando fizer exercícios, beba água com mais frequência.",
                "Água saborizada com rodelas de limão, hortelã ou gengibre é uma alternativa ao refrigerante.",
            ]),
            ("🥪", "Lanches saudáveis e práticos", [
                "Frutas fáceis de levar, como banana, maçã, mexerica e uva.",
                "Castanhas, amendoim sem sal ou mix de sementes.",
                "Palitos de cenoura, pepino ou tomatinhos.",
                "Iogurte natural com fruta picada.",
                "Pipoca feita em casa, com pouco óleo e sal.",
            ]),
            ("🛒", "Dicas gerais", [
                "Prefira alimentos frescos e pouco processados aos ultraprocessados (salgadinhos, biscoitos recheados, embutidos).",
                "Leia os rótulos: quanto menor e mais conhecida a lista de ingredientes, melhor.",
                "Planeje as compras e as refeições da semana para evitar escolhas de última hora.",
            ]),
        ],
    },
    "exercicios": {
        "cor": "roxo",
        "icone": "🚶",
        "titulo": "Caminhadas e exercícios",
        "resumo": "Benefícios da caminhada, como começar, horários e cuidados.",
        "introducao": (
            "A caminhada é uma das formas mais simples de se movimentar: não precisa "
            "de equipamento caro e pode ser feita no seu ritmo."
        ),
        "secoes": [
            ("💚", "Benefícios da caminhada", [
                "Faz bem para o coração e para a circulação.",
                "Ajuda a aliviar o estresse e melhora o humor.",
                "Contribui para um sono mais profundo.",
                "Aumenta a disposição e fortalece músculos e articulações.",
                "Pode ser um momento de convivência com amigos, família ou com o seu cachorro.",
            ]),
            ("👟", "Como começar", [
                "Comece devagar, com caminhadas curtas, e aumente o tempo aos poucos, conforme se sentir bem.",
                "Ande num ritmo em que você ainda consiga conversar.",
                "Coloque o movimento na rotina: desça um ponto antes, use escadas, caminhe nas ligações.",
                "Escolha um trajeto agradável e, se puder, chame alguém para ir junto.",
                "Faça alongamentos leves antes e depois.",
            ]),
            ("⏰", "Melhores horários", [
                "O melhor horário é aquele que cabe na sua rotina e que você consegue manter.",
                "De manhã, a luz do sol ajuda a acordar e a regular o sono.",
                "No fim da tarde, a caminhada ajuda a relaxar depois do trabalho.",
                "Em dias quentes, evite o sol do fim da manhã e do começo da tarde.",
                "Evite exercícios intensos logo antes de dormir.",
            ]),
            ("⚠️", "Cuidados", [
                "Use tênis confortável e roupas leves.",
                "Beba água antes, durante e depois da atividade.",
                "Use protetor solar e boné ou chapéu.",
                "Prefira lugares seguros, planos e bem iluminados.",
                "Pare e procure atendimento se sentir dor no peito, falta de ar forte, tontura ou mal-estar.",
                "Se você tem algum problema de saúde (coração, pressão, diabetes, articulações) "
                "ou está grávida, converse com um médico antes de começar.",
            ]),
        ],
    },
}
