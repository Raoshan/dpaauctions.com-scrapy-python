import scrapy
import pandas as pd
df = pd.read_csv('F:\Web Scraping\Golabal\keywords.csv')
# base_url = 'https://www.dpaauctions.com/servlet/Search.do?status=offline&keywordFields=lotId&keywordFields=controlNumber&keywordFields=autoIdNum&keywordFields=RECity&RESearch=true&keyword={}&categoryName=&REState=&distance=&searchLocation='
base_url = 'https://www.dpaauctions.com/servlet/Search.do?auctionId=&keywordFields=lotId&keywordFields=controlNumber&keywordFields=autoIdNum&keywordFields=RECity&noCache=false&distance=&searchLocation=&RESearch=true&REState=&keyword={}&categoryName=&status=offline&page=1&perPage=20&orderBy='

class DpaSpider(scrapy.Spider):
    name = 'dpa'
    def start_requests(self):
        for index in df:
            yield scrapy.Request(url=base_url.format(index), callback=self.parse, cb_kwargs={'index':index})

    def parse(self, response, index):
        total_pages = response.xpath("//div[@class='dpa-search-pagination-wrap']/ul/li[last()-1]/a/text()").get()             
        current_page =response.css("a.search-nav-pages--selected::text").get()  
        url = response.url 
       
        if total_pages and current_page:           
            if int(current_page) ==1:
                for i in range(2, int(total_pages)+1): 
                    min = 'page='+str(i-1)
                    max = 'page='+str(i)
                    url = url.replace(min,max)   
                    # print(url)                                                               
                    yield response.follow(url, cb_kwargs={'index':index})

        links = response.xpath("//div[@class='panel search-item-container']/a/@href ")   
        for link in links:            
            yield response.follow("https://www.dpaauctions.com"+link.get(), callback=self.parse_item, cb_kwargs={'index':index})  

    def parse_item(self, response, index): 
        print(".................")          
        product_url = response.url
        print(product_url)  
        product_name = response.css(".search-item-title a::text").get().strip()
        print(product_name)         
        image = "https://www.dpaauctions.com"+response.css(".main-prod-img img::attr(src)").get()     
        print(image)  
        
        location = response.css(".search-item-location p::text").get().strip() 
       
        print(location)
        auction1 = response.xpath("//div[@class='search-item-subsection search-item-time']/p[2]/text()").get()
        auction2 = auction1.split('|')
        auction_date = auction2[0].strip()
        print(auction_date)        
       
        lot = response.css(".search-item-id::text").get().strip()        
        lot_number = lot[5:]
        print(lot_number)
        auctioner = response.xpath('//*[@id="post-26299"]/div/div[1]/div/div[2]/div[1]/div/div[2]/div[1]/p[2]/a[2]/text()').get()
        print(auctioner)
        des = response.xpath('//*[@id="post-26299"]/div/div[1]/div/div[2]/div[1]/div/div[2]/div[1]/text()[2]').get()
        description = des.strip()
        print(description)
        
        yield{
            
            'product_url' : response.url,           
            'item_type' :index.strip(),            
            'image_link' : image,          
            'auction_date' : auction_date,            
            'location' : location,           
            'product_name' : product_name,            
            'lot_id' : lot_number,          
            'auctioner' : auctioner,
            'website' : 'dpaauctions',
            'description' : description             
        }