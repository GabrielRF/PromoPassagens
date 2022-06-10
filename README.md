# [PromoPassagens](https://t.me/PromoPassagens)

Canal público no Telegram que reúne promoções de passagens aéreas coletadas em uma lista no Twitter.

## Configuração:

Defina as variáveis na aba `Secrets` do repositório:

`BOT_TOKEN`: Token do bot que enviará as mensagens no canal. Fornecido pelo [@BotFather](https://t.me/BotFather);

`DESTINATION`: Canal público que receberá as mensagens. Exemplo: `PromoPassagens` (não use `@`!);

`TWITTER_ACCESS_SECRET`: Valor fornecido pelo Twitter em `https://developer.twitter.com/en/portal/dashboard`;

`TWITTER_ACCESS_TOKEN`: Valor fornecido pelo Twitter em `https://developer.twitter.com/en/portal/dashboard`;

`TWITTER_CONSUMER_KEY`: Valor fornecido pelo Twitter em `https://developer.twitter.com/en/portal/dashboard`;

`TWITTER_CONSUMER_SECRET`: Valor fornecido pelo Twitter em `https://developer.twitter.com/en/portal/dashboard`;

`TWITTER_OWNER`: Perfil criador da lista no Twitter. Exemplo: `GabRF`;

`TWITTER_SLUG`: Slug da lista no Twitter. Exemplo: `canal-promopassagens`.

## Uso

A ação irá buscar as atualizações a cada 15 minutos conforme definido no arquivo [cron.yml](.github/workflows/cron.yml).
