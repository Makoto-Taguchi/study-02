import os
from selenium.webdriver import Chrome, ChromeOptions
import time
import pandas as pd
import datetime
from webdriver_manager.chrome import ChromeDriverManager


now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
logfile_name = './log/log_' + now + '.txt'
outputfile_name = './log/output_{date}_{keyword}.csv'

# ログファイルへの書き込みする関数
def log(txt):
    with open(logfile_name, 'a')as f:
        f.write(txt + '\n')

# テーブルのthタグからtargetの文字列を探して、対応するtdを返す関数
def find_table_target_word(th_elms, td_elms, target:str):
    for th_elm,td_elm in zip(th_elms,td_elms):
        if th_elm.text == target:
            return td_elm.text


# Chromeを起動する関数
def set_driver(driver_path, headless_flg):
    # Chromeドライバーの読み込み
    options = ChromeOptions()

    # ヘッドレスモード（画面非表示モード）をの設定
    if headless_flg == True:
        options.add_argument('--headless')

    # 起動オプションの設定
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
    # options.add_argument('log-level=3')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')          # シークレットモードの設定を付与

    # ChromeのWebDriverオブジェクトを作成する。
    # return Chrome(executable_path=os.getcwd() + "/" + driver_path, options=options)
    return Chrome(ChromeDriverManager().install(), options=options)


# main処理
def main():
    search_keyword = input("検索ワードを入力してください：")
    log(f'検索ワード："{search_keyword}"')
    # driverを起動
    if os.name == 'nt': #Windows
        driver = set_driver("chromedriver.exe", False)
    elif os.name == 'posix': #Mac
        driver = set_driver("chromedriver", False)
    # Webサイトを開く
    driver.get("https://tenshoku.mynavi.jp/")
    time.sleep(5)

    try:
        # ポップアップを閉じる
        driver.execute_script('document.querySelector(".karte-close").click()')
        time.sleep(5)
        # ポップアップを閉じる
        driver.execute_script('document.querySelector(".karte-close").click()')
    except:
        pass
    
    # 検索窓に入力
    driver.find_element_by_class_name(
        "topSearch__text").send_keys(search_keyword)
    # 検索ボタンクリック
    driver.find_element_by_class_name("topSearch__button").click()

    # ページ終了まで繰り返し取得
    exp_name_list = []
    exp_status_list = []
    exp_income_list = []
    count = 1
    success = 0
    fail = 0

    while True:
        name_list = driver.find_elements_by_class_name("cassetteRecruit__name")
        status_list = driver.find_elements_by_css_selector(".cassetteRecruit__heading .labelEmploymentStatus")
        table_list = driver.find_elements_by_css_selector(".cassetteRecruit .tableCondition")


        # 1ページ分繰り返し
        print(len(name_list))
        for name, status, table in zip(name_list, status_list, table_list):
            # 例外発生時も処理を継続する
            try:
                # 会社名のみ抽出する処理（スライス）
                target ='|'
                idx = name.text.find(target)
                r = name.text[:idx]

                exp_name_list.append(r)
                # print(r)

                exp_status_list.append(status.text)
                # print(status.text)

                income = find_table_target_word(table.find_elements_by_tag_name("th"), table.find_elements_by_tag_name("td"), "初年度年収")
                exp_income_list.append(income)
                # print(income)

                # ログ書き込み
                log(f'{count} 件目成功： {r}')
                success += 1
            except Error as e:
                # ログ書き込み
                log(f'{count} 件目失敗： {name.text}')
                fail += 1
            finally:
                count += 1


        # 次ページのボタンがなければ終了
        next_page = driver.find_elements_by_css_selector(".pager__next .iconFont--arrowLeft")
        if len(next_page) >= 1:
            next_page_link = next_page[0].get_attribute("href")
            driver.get(next_page_link)
            time.sleep(5)
        else:
            print("最終ページです。終了します。")
            break
    
    # CSVに出力
    # df = pd.DataFrame([exp_name_list,exp_status_list,exp_income_list], columns=["会社名", "就業形態", "初年度年収"])
    df = pd.DataFrame({"会社名":exp_name_list,
                        "就業形態":exp_status_list,
                        "初年度年収":exp_income_list})
    print(df)
    df.to_csv(outputfile_name.format(date=now,keyword=search_keyword))
    print("CSVへの出力処理終了しました。")
    log(f'成功件数：{success}件、失敗件数：{fail}件')



# 直接起動された場合はmain()を起動(モジュールとして呼び出された場合は起動しないようにするため)
if __name__ == "__main__":
    main()
