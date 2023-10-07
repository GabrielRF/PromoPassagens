# [PromoPassagens](https://t.me/PromoPassagens)

Canal público no Telegram que reúne promoções de passagens aéreas coletadas em uma lista no Twitter.

## Configuração:

Defina as variáveis na aba `Secrets` do repositório:

`BOT_TOKEN`: Token do bot que enviará as mensagens no canal. Fornecido pelo [@BotFather](https://t.me/BotFather);

`DESTINATION`: Canal público que receberá as mensagens. Exemplo: `@PromoPassagens`.

## Uso

Copie uma das ações da pasta `.github/workflows` e personalize o arquivo, ajustando o seu nome, o nome da ação na Linha 1 e a url do feed rss na linha 26, em `URL`.

A ação irá buscar as atualizações a cada hora conforme definido no ação.
