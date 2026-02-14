function onInstall(e) {
  onOpen(e);
}

function onOpen() {
  DocumentApp.getUi()
    .createAddonMenu()
    .addItem('Open Sidebar', 'openSidebar')
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
    .setText('Open Encypher Sidebar')
    .setTextButtonStyle(CardService.TextButtonStyle.FILLED)
    .setOnClickAction(action);

  var section = CardService.newCardSection()
    .addWidget(CardService.newTextParagraph().setText('Sign and verify selected or full Google Docs content with Encypher provenance.'))
    .addWidget(openButton);

  return CardService.newCardBuilder()
    .setHeader(CardService.newCardHeader().setTitle('Encypher Provenance'))
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
    .setTitle('Encypher Provenance')
    .setWidth(360);
  DocumentApp.getUi().showSidebar(html);
}
