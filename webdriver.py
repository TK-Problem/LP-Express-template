from pyppeteer import launch
import time


async def create_browser():
    browser = await launch(handleSIGINT=False, handleSIGTERM=False, handleSIGHUP=False,
                           options={'args': ['--no-sandbox']})
    page = await browser.newPage()
    return browser, page


async def wait_till_appears(page, xpath, seconds=10):
    for i in range(seconds*2):
        e = await page.xpath(xpath)
        if e:
            break
        time.sleep(0.5)


async def login(page, usr, psw):
    # go to page
    await page.goto("https://lpexpress.lt/home")

    # wait till cookie appears
    await wait_till_appears(page, "//a[@id='CybotCookiebotDialogBodyLevelButtonAccept']")
    # click cookie button
    await page.click('div[id="CybotCookiebotDialogBodyLevelButtonAcceptWrapper"]')
    # click login button
    await page.click(".login-name")

    # wait till appears
    await wait_till_appears(page, "//input[@formcontrolname='username']")
    # enter text
    await page.type("input[formcontrolname='username']", usr)
    await page.type("input[formcontrolname='password']", psw)

    # click login button
    await page.click("button[type='submit']")

    time.sleep(2)
    await page.screenshot({'path': 'test_1.png'})

    # get page source
    response = await page.content()

    # check if login was successful
    if 'Pridėti siuntą' in str(response):
        return page, True
    else:
        return page, False


async def upload_data(page):

    # wait till add parcel button appears
    await wait_till_appears(page, "//a[contains(text(), 'Pridėti siuntą')]")
    # click add parcel
    await page.click("a[role='button']")

    # wait till cookie appears
    await wait_till_appears(page, "//a[@id='CybotCookiebotDialogBodyLevelButtonAccept']")
    # click cookie button
    await page.click('div[id="CybotCookiebotDialogBodyLevelButtonAcceptWrapper"]')

    # wait till mail button appears
    await wait_till_appears(page, "//span[contains(text(), 'Pašto')]")
    # click mail button
    _ = "ul.list-checkbox:nth-child(3) > li:nth-child(3) > label:nth-child(1) > span:nth-child(3)"
    await page.click(_)

    time.sleep(2)

    await page.screenshot({'path': 'test_2.png'})

