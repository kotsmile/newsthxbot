from news_dumper import dump_all, save_to_db, boards_path, db_path

if __name__ == '__main__':
    print('Start dunmping')
    news_df = dump_all(boards_path)
    save_to_db(news_df, db_path)
    print('Done!')