from pyppeteer import launch
import time
import pandas as pd


async def create_browser():
    """
    This function creates pyppeteer browser object and page.
    :return:
    """
    browser = await launch(handleSIGINT=False, handleSIGTERM=False, handleSIGHUP=False,
                           options={'args': ['--no-sandbox']})
    page = await browser.newPage()
    return browser, page


async def close_browser(browser):
    """
    This functions closes and relaunches browser.
    :param browser:
    :return:
    """
    await browser.close()
    return await create_browser()


async def wait_till_appears(page, xpath, seconds=10):
    for i in range(seconds):
        e = await page.xpath(xpath)
        if e:
            break
        time.sleep(1)


async def login_to_lpe(page, usr, psw):
    """
    This function logins to LP-express website.
    :param page: pyputter page object
    :param usr:
    :param psw:
    :return:
    """
    # go to page
    await page.goto("https://lpexpress.lt/home")
    # artificially slow down
    time.sleep(2)

    # wait till Christmas message appears
    # await wait_till_appears(page, "//button[@aria-label='Close']")
    # close pop-up
    # await page.click('button[aria-label="Close"]', {'delay': 100})

    # wait till cookie appears
    await wait_till_appears(page, "//a[@id='CybotCookiebotDialogBodyLevelButtonAccept']")
    # click cookie button
    await page.click('div[id="CybotCookiebotDialogBodyLevelButtonAcceptWrapper"]')
    # click login button
    await page.click(".login-name", {'delay': 100})

    # wait till appears
    await wait_till_appears(page, "//input[@formcontrolname='username']")
    # enter text
    await page.type("input[formcontrolname='username']", usr)
    await page.type("input[formcontrolname='password']", psw)

    # click login button
    await page.click("button[type='submit']", {'delay': 100})

    # wait till "Pridėti siuntą" button appears
    await page.waitForSelector("a[role='button']", timeout=30000)
    await wait_till_appears(page, "//a[contains(text(), 'Pridėti siuntą')]")

    # get page source
    response = await page.content()

    return page, str(response)


async def upload_parcel(page, row):
    """
    This function uploads parcel based on Etsy data
    :param page: pyppeteer object
    :param row: pandas Series
    :return: None
    """
    if isinstance(row, str):
        _index = ['Pardavimo data', 'Siuntinio vertė', 'Siuntinio tipas',
                  'Siuntinio svoris', 'Siuntinio tūris', 'Pirmenybinis',
                  'Gavėjas', 'Šalis', 'Miestas', 'Adreso eilutė 1', 'Adreso eilutė 2',
                  'Pašto kodas', 'Pristatymo pastabos']

        _data = [1, 2, 'S', 150, 5, 1, 'Peter Peterson', 'Jungtinės Amerikos Valstijo', 'Paris',
                 'Streetname', '1-1', '11123', 'mail@mail.com']
        row = pd.Series(pd.Series(_data, index=_index))

    """
    Step 1
    """
    # wait till add parcel button appears
    # await wait_till_appears(page, "//a[contains(text(), 'Pridėti siuntą')]")
    await page.waitForSelector("a[role='button']", timeout=30000)
    # click add parcel
    await page.click("a[role='button']", {'delay': 100})
    time.sleep(0.1)

    # await page.screenshot({'path': f'step_1.png'})
    print('1/5')

    """
    Step 2
    """
    time.sleep(0.5)
    # wait till mail button appears
    # await wait_till_appears(page, "//span[contains(text(), 'Pašto')]")
    # click mail button
    _ = "ul.list-checkbox:nth-child(3) > li:nth-child(3) > label:nth-child(1) > span:nth-child(3)"
    await page.waitForSelector(_, timeout=30000)
    await page.click(_, {'delay': 100})
    time.sleep(0.5)

    # click address
    _ = "ul.list-checkbox:nth-child(5) > li:nth-child(1) > label:nth-child(1) > span:nth-child(3)"
    await page.click(_, {'delay': 100})
    time.sleep(0.5)

    # click small package
    if row['Siuntinio tipas'] == 'S':
        _ = "ul.list-checkbox:nth-child(7) > li:nth-child(1)"
    # click medium package
    else:
        _ = "ul.list-checkbox:nth-child(7) > li:nth-child(2)"

    # click selected package element
    await page.waitForSelector(_, timeout=30000)
    await page.click(_, {'delay': 100})

    # add weight
    # await wait_till_appears(page, "//input[@id='weight']")
    await page.waitForSelector("input[id='weight']", timeout=30000)
    await page.type("input[id='weight']", str(int(row['Siuntinio svoris'])/1000))
    time.sleep(0.1)
    # wait till button loads
    # _ = "//a[@class='btn btn-default btn-tooltip btn-sm text-uppercase ld-ext-right btn-ico-right']"
    # await wait_till_appears(page, _)

    # await page.screenshot({'path': f'step_2.png'})
    print('2/5')

    # click NEXT button
    await page.waitForSelector("a.btn-default:nth-child(1)", timeout=30000)
    await page.click("a.btn-default:nth-child(1)", {'delay': 100})

    """
    Step 3
    """
    time.sleep(0.5)
    # wait till input fields are loaded
    # await wait_till_appears(page, "//input[@formcontrolname='recipient']")

    # type recipient's name
    await page.waitForSelector("input[formcontrolname = 'recipient']", timeout=30000)
    await page.type("input[formcontrolname = 'recipient']", row['Gavėjas'])
    time.sleep(0.1)

    # click on placeholder
    await page.waitForSelector("input[placeholder = 'Šalis']", timeout=30000)
    await page.click("input[placeholder = 'Šalis']", {'delay': 100})
    time.sleep(0.1)

    # enter country name
    await page.waitForSelector("input[placeholder = 'Šalis']", timeout=30000)
    await page.type("input[placeholder = 'Šalis']", row['Šalis'])
    time.sleep(1)
    await page.keyboard.press('Tab')

    # type recipient's city
    await page.waitForSelector("input[placeholder = 'Įrašykite vietovę']", timeout=30000)
    await page.type("input[placeholder = 'Įrašykite vietovę']", row['Miestas'])
    time.sleep(0.1)

    # type recipient's Address 1
    await page.type("input[formcontrolname = 'address1']", f"{row['Adreso eilutė 1']}")
    time.sleep(0.1)

    # type recipient's Address 2
    await page.type("input[formcontrolname = 'address2']", f"{row['Adreso eilutė 2']}")
    time.sleep(0.1)

    # add post code
    await page.type("input[formcontrolname = 'postalCode']", f"{row['Pašto kodas']}")
    time.sleep(0.1)

    # add e-mail
    await page.waitForSelector("input[formcontrolname = 'email']", timeout=30000)
    await page.type("input[formcontrolname = 'email']", row['Pristatymo pastabos'])
    # await page.type("input[formcontrolname = 'email']", 'mail@mail.com')
    time.sleep(0.1)
    # wait till button loads
    # _ = "//a[@class='btn btn-default btn-sm text-uppercase ld-ext-right btn-ico-right']"
    # await wait_till_appears(page, _)

    # await page.screenshot({'path': f'step_3.png'})
    print('3/5')

    # click NEXT button
    await page.waitForSelector("a.btn-default:nth-child(1)", timeout=30000)
    await page.click("a.btn-default:nth-child(1)", {'delay': 100})

    """
    Step 4
    """
    time.sleep(0.5)
    # wait till prices appear
    # await wait_till_appears(page, '//label[@class="service-title"]')

    # find buttons and price elements
    await page.waitForSelector('label[class = "service-title"]', timeout=30000)
    buttons = await page.xpath('//label[@class="service-title"]')
    await page.waitForSelector('label[class = "service-price"]', timeout=30000)
    prices = await page.xpath('//label[@class="service-price"]')

    # get prices
    price_su_sekimu = await page.evaluate('(element) => element.textContent', prices[1])
    price_pasirasytinai = await page.evaluate('(element) => element.textContent', prices[2])

    # select the right option
    if row['Pirmenybinis']:
        # transform prices to floats
        price_su_sekimu = float(price_su_sekimu[:-2].replace(',', '.'))
        price_pasirasytinai = float(price_pasirasytinai[:-2].replace(',', '.'))

        # su sekimu price is less than pasirasytinai plus 0.2 then select option 1
        if price_su_sekimu <= price_pasirasytinai + 0.2:
            await buttons[1].click()
        else:
            await buttons[1].click()
    else:
        # click first option
        await buttons[0].click()

    # wait till button loads
    # _ = "//a[@class='btn btn-default btn-sm text-uppercase ld-ext-right btn-ico-right']"
    # await wait_till_appears(page, _)

    # click NEXT button
    await page.waitForSelector("a.btn-default:nth-child(1)", timeout=30000)
    await page.click("a.btn-default:nth-child(1)", {'delay': 100})

    time.sleep(1)

    # wait till add parcel button appears
    await page.waitForSelector("a[role='button']", timeout=30000)
    await wait_till_appears(page, "//a[contains(text(), 'Pridėti siuntą')]")

    await page.keyboard.press('Home')
    time.sleep(1)
    # await page.screenshot({'path': f'step_4.png'})
    print('4/5')

    """
    Step 5 check whatever new form is available
    """
    if row['Šalis'] in ['Jungtinės Amerikos Valstijos', 'Didžioji Britanija', 'Norvegija']:
        await page.waitForSelector('i[class="ico v-m svg-add-document-red ico-margin"]', timeout=30000)
        await wait_till_appears(page, "//span[contains(text(), 'Pildyti')]", seconds=15)

        e = await page.xpath("//span[contains(text(), 'Pildyti')]")
        if e:
            await e[0].click({'delay': 100})
            time.sleep(0.5)
            """
            Step 6
            """
            # wait till page loads
            # await wait_till_appears(page, "// label[contains(text(), 'Siuntos turinys')]")

            # click select Dovana option
            await page.waitForSelector('select[formcontrolname="parcelType"]', timeout=30000)
            await page.select('select[formcontrolname="parcelType"]', 'GIFT')
            time.sleep(0.1)

            # type "Toy" for summary
            await page.type('input[formcontrolname = "summary"]', 'Toy', {'delay': 100})
            time.sleep(0.1)

            # type 1 for quantity
            await page.type('input[formcontrolname = "quantity"]', '1', {'delay': 100})
            time.sleep(0.1)

            # type parcel's weight
            await page.type('input[formcontrolname = "weight"]', f"{int(row['Siuntinio svoris'])}", {'delay': 100})
            time.sleep(0.1)

            # type parcel's price
            await page.type('input[formcontrolname = "amount"]', "5", {'delay': 100})
            time.sleep(0.1)

            # parcel origin, always Lithuania
            await page.select('select[formcontrolname="countryId"]', '118')
            time.sleep(0.1)

            # wait till button to continue appears
            await wait_till_appears(page, "//button[contains(text(), 'Saugoti')]")
            time.sleep(0.1)
            # await page.screenshot({'path': f'step_51.png'})
            print('5.1/5')

            # click NEXT button
            await page.waitForSelector("button.btn-default", timeout=30000)
            await page.click("button.btn-default", {'delay': 100})

            # await till 'Pildyti' button is loaded
            # await wait_till_appears(page, "//span[contains(text(), 'Pildyti')]", seconds=3)
            time.sleep(1)

    # await page.screenshot({'path': f'step_5.png'})
    time.sleep(0.1)
    print('5/5')

    # get page source
    response = await page.content()

    # reload page
    await page.reload()

    return page, response


async def upload_all_parcel(page, df):
    """
    This function iterates over all orders
    :param page:
    :param df:
    :return:
    """
    for idx in df.index:
        row = df.loc[idx]
        page, _ = await upload_parcel(page, row)
        print(df.loc[idx, 'Gavėjas'], f"{idx + 1}/{len(df)}")
        # reload page
        await page.reload()
        time.sleep(2)
        # current page
        # await page.screenshot({'path': f'step_6.png'})

    response = await page.content()

    return page, response

