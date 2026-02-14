function onInstall(e) {
  onOpen(e);
}

function onOpen() {
  DocumentApp.getUi()
    .createAddonMenu()
    .addItem('Open C2PA Sidebar', 'openSidebar')
    .addSeparator()
    .addItem('Sign Selection', 'signCurrentSelection')
    .addItem('Sign Full Document', 'signFullDocument')
    .addSeparator()
    .addItem('Verify Selection', 'verifyCurrentSelection')
    .addItem('Verify Full Document', 'verifyFullDocument')
    .addToUi();
}

function onDocsHomepage() {
  var action = CardService.newAction().setFunctionName('openSidebarFromCard');
  var openButton = CardService.newTextButton()
    .setText('Open C2PA Provenance Sidebar')
    .setTextButtonStyle(CardService.TextButtonStyle.FILLED)
    .setOnClickAction(action);

  var section = CardService.newCardSection()
    .addWidget(CardService.newTextParagraph().setText('Embed and verify cryptographic proof of origin in Google Docs with Encypher C2PA provenance workflows.'))
    .addWidget(openButton);

  return CardService.newCardBuilder()
    .setHeader(CardService.newCardHeader().setTitle('Encypher C2PA Provenance'))
    .addSection(section)
    .build();
}

function openSidebarFromCard() {
  openSidebar();
  return CardService.newActionResponseBuilder()
    .setNavigation(CardService.newNavigation().popToRoot())
    .build();
}

function openSidebarFromUniversalAction() {
  openSidebar();
  return CardService.newUniversalActionResponseBuilder()
    .displayAddOnCards([
      onDocsHomepage()
    ])
    .build();
}

function openSidebar() {
  var template = HtmlService.createTemplateFromFile('Sidebar');
  var html = template.evaluate()
    .setTitle('Encypher C2PA Provenance')
    .setWidth(360);
  DocumentApp.getUi().showSidebar(html);
}
