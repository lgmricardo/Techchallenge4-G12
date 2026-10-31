# Fontes embutidas

**DejaVu Sans** (e DejaVu Sans Mono), usadas na geração do PDF do relatório técnico.

**Por que estão aqui.** As fontes padrão do reportlab (Helvetica, Courier) não trazem os glifos que este relatório precisa: os expoentes `⁻⁸` dos p-valores, `ρ` (Spearman), `×` e `≥`.

*O símbolo de rupia (U+20B9) também exigia fonte própria, mas deixou de ser usado: por decisão de 24/09/2026, valores monetários são publicados sem símbolo, com a moeda declarada em texto. A fonte continua necessária pelos demais glifos.* Sem elas, esses caracteres saem como quadrados pretos no PDF.

Embutir a fonte mantém a geração reproduzível em qualquer máquina, sem depender do que estiver instalado no sistema.

**Licença:** DejaVu Fonts License (derivada da Bitstream Vera), que permite redistribuição. https://dejavu-fonts.github.io/License.html
