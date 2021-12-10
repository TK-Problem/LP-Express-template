from pyppeteer import launch
import time


async def create_browser():
    browser = await launch(handleSIGINT=False, handleSIGTERM=False, handleSIGHUP=False,
                           options={'args': ['--no-sandbox']})
    page = await browser.newPage()
    return browser, page


# async def close_browser(browser):
#     await browser.close()


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
    # await page.screenshot({'path': 'test_1.png'})

    # get page source
    response = await page.content()

    return page, str(response)


async def upload_data(page):
    """
    Step 1
    """
    # wait till add parcel button appears
    await wait_till_appears(page, "//a[contains(text(), 'Pridėti siuntą')]")
    # click add parcel
    await page.click("a[role='button']")

    """
    Step 2
    """
    # wait till cookie appears
    await wait_till_appears(page, "//a[@id='CybotCookiebotDialogBodyLevelButtonAccept']")
    # click cookie button
    await page.click('div[id="CybotCookiebotDialogBodyLevelButtonAcceptWrapper"]')

    # wait till mail button appears
    await wait_till_appears(page, "//span[contains(text(), 'Pašto')]")
    # click mail button
    _ = "ul.list-checkbox:nth-child(3) > li:nth-child(3) > label:nth-child(1) > span:nth-child(3)"
    await page.click(_)
    # click address
    _ = "ul.list-checkbox:nth-child(5) > li:nth-child(1) > label:nth-child(1) > span:nth-child(3)"
    await page.click(_)
    # click small package
    _ = "ul.list-checkbox:nth-child(7) > li:nth-child(1)"
    await page.click(_)
    # add weight
    await wait_till_appears(page, "//input[@id='weight']")
    await page.type("input[id='weight']", '0.1')
    # wait till button loads
    _ = "//a[@class='btn btn-default btn-tooltip btn-sm text-uppercase ld-ext-right btn-ico-right']"
    await wait_till_appears(page, _)
    # click NEXT button
    await page.click("a.btn-default:nth-child(1)")

    """
    Step 3
    """
    # wait till input fields are loaded
    await wait_till_appears(page, "//input[@formcontrolname='recipient']")
    # type recipient's name
    await page.type("input[formcontrolname = 'recipient']", 'Peter Peterson')
    # click on placeholder
    await page.click("input[placeholder = 'Šalis']")
    # enter country name
    await page.type("input[placeholder = 'Šalis']", 'Prancūzija')
    time.sleep(1)
    await page.keyboard.press('Tab')
    # type recipient's city
    await page.type("input[placeholder = 'Įrašykite vietovę']", 'Paris')
    # type recipient's Adress 1
    await page.type("input[formcontrolname = 'address1']", 'Streetname')
    # type recipient's Adress 2
    await page.type("input[formcontrolname = 'address2']", '1-1')
    # add post code
    await page.type("input[formcontrolname = 'postalCode']", '11123')
    # add e-mail
    await page.type("input[formcontrolname = 'email']", 'mail@mail.com')
    # wait till button loads
    _ = "//a[@class='btn btn-default btn-sm text-uppercase ld-ext-right btn-ico-right']"
    await wait_till_appears(page, _)
    # click NEXT button
    await page.click("a.btn-default:nth-child(1)")
    """
    Step 4
    """
    # wait till prices appear
    await wait_till_appears(page, '//label[@class="service-price"]')
    # click first option
    await page.click("div[class= 'row service-header']")
    # wait till button loads
    _ = "//a[@class='btn btn-default btn-sm text-uppercase ld-ext-right btn-ico-right']"
    await wait_till_appears(page, _)
    # click NEXT button
    await page.click("a.btn-default:nth-child(1)")

