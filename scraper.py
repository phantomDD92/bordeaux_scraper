from playwright.sync_api import expect, sync_playwright
import re
import json
from twocaptcha import TwoCaptcha

solver = TwoCaptcha('CAPTCHA_SOLVER_KEY')
MAIN_URL = "https://www.bunnings.com.au"

class BunningsScraper():
    def __init__(self):
        with open("api.js", "rt") as f:
            self.payload = f.read()
        pass
    
    def get_text(self, tag):
        return tag.text_content().strip().replace(",", " ")
    
    def scrape_content(self):
        print(f"Name, School, Job Description, Department, Earnings, Year", file=self.csvfile)
        self.page.wait_for_selector("#page-results")
        table_tag = self.page.get_by_role('table')
        for row in table_tag.locator('tr').all():
            cells = row.locator('td').all()
            if len(cells) >= 6: 
                print(f"{self.get_text(cells[0])}, {self.get_text(cells[1])}, {self.get_text(cells[2])}, {self.get_text(cells[3])}, {self.get_text(cells[4])}, {self.get_text(cells[5])}", file=self.csvfile)

    def modify_apijs(self, route):
        route.fulfill(body = self.payload)
        
    def handle_console(self, msg):
        if "intercepted-params:" in msg.text:
            params = json.loads(msg.text.replace("intercepted-params:", ""))
            print(params)
            result = solver.turnstile(sitekey=params['sitekey'],
                            url=params['pageurl'], 
                            data=params['data'],
                            pagedata=params['pagedata'],
                            action=params['action'],
                            useragent=params['userAgent'])
            print(result)
            self.page.evaluate("(token) => { cfCallback(token);}", result['code']); 
            

    def start(self):
        self.csvfile = open('./result.csv', 'w', encoding='utf-8')
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=True
        )
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.page.route(re.compile(r".+api.js\?onload=lDtWXt4.+"), self.modify_apijs)
        self.page.on('console', self.handle_console)
        self.page.goto(MAIN_URL, timeout=60000)
        self.page.wait_for_load_state('load')
        self.page.wait_for_timeout(2000000)
        self.csvfile.close()
        self.context.close()
        self.browser.close()

def main():
    extractor = BunningsScraper()
    extractor.start()
    
if __name__ == "__main__":
    main()
