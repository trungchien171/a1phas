# run directly on script
from Trung_Chien_datamodel import TradingData
from Trung_Chien_MomentumHSI_posgen import GeneratePosition
import telegram
import asyncio
import os

async def main():
    trading_data = TradingData( 
        symbol='vn30f1m',
        csv_file=r'D:\Quantitative Research\H-Tech\05-07-2024\paper_trade_to_csv\vn30f1m_paper_trade.csv'
    )

    pos_gen = GeneratePosition()
    bot = telegram.Bot(token='7117934389:AAFvk_lHb-kKg8Z75z2gZ4NwSjIleetHjdQ')

    df = trading_data.get_vn30f1m_trading()
    trading_data.update_data(df)
    feature = pos_gen.get_feature()
    position = pos_gen.posgen(feature)

    if position is not None:
        updated_df = trading_data.update_position(position)
        message = updated_df[['Date', 'Close', 'Position']].tail(1).to_string(index=False)
        await bot.send_message(chat_id='-4270845760', text=f'<pre>{message}</pre>', parse_mode='HTML')
        print(updated_df)
    else:
        print("Failed to update the position")

if __name__ == "__main__":
    asyncio.run(main())

# run using aws lambda function
# import pandas as pd
# import os
# import telegram
# import asyncio
# from datetime import datetime, timedelta
# from Trung_Chien_datamodel import TradingData
# from Trung_Chien_MomentumHSI_posgen import GeneratePosition

# bot = telegram.Bot(token='7117934389:AAFvk_lHb-kKg8Z75z2gZ4NwSjIleetHjdQ')

# async def send_message(message):
#     await bot.send_message(chat_id='-4270845760', text=f'<pre>{message}</pre>', parse_mode='HTML')

# def lambda_handler(event, context):
#     trading_data = TradingData(
#         symbol='vn30f1m',
#         csv_file=r'D:\Quantitative Research\H-Tech\Alpha\Alpha_Paper_Trade\TrungChien\vn30f1m_alpha\vn30f1m_paper_trade.csv'
#     )

#     pos_gen = GeneratePosition()

#     df = trading_data.get_vn30f1m_trading()
#     trading_data.update_data(df)
#     feature = pos_gen.get_feature()
#     position = pos_gen.posgen(feature)

#     if position is not None:
#         updated_df = trading_data.update_position(position)
#         message = updated_df[['Date', 'close', 'Position']].tail(1).to_string(index=False)
#         asyncio.run(send_message(message))
#         print(updated_df)
#     else:
#         print("Failed to update the position")

#     return {
#         'statusCode': 200,
#         'body': 'Function executed successfully'
#     }
