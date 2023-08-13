import datetime
import os
from model import UserTrade, Trade, User
import controller
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "email" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/login', methods=['GET', 'POST'])
def login():
    print(os.environ.get("SECRET_KEY"))
    if 'email' in session:
        return redirect('/')

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.check_login_credentials(email, password)
        if user:
            session['email'] = email
            return redirect('/')

    return render_template('login.html')


@app.route('/')
@login_required
def index():
    current_date = datetime.date.today()

    trades = Trade.get_all()
    user_trades = UserTrade.get_all(user_id=1)

    stocks = ['SPY', 'QQQ', 'DIA']
    stock_data = []

    for stock_symbol in stocks:
        live_price, date_labels, value_labels = controller.get_chart_data(stock_symbol)
        stock_data.append({
            'stock_symbol': stock_symbol,
            'live_price': round(live_price, 2),
            'date_labels': date_labels,
            'value_labels': value_labels,
        })

    return render_template('trades.html', user_trades=user_trades, current_date=current_date, stock_data=stock_data, trades=trades, active_page='trade-ideas')


@app.route('/trades-tracker')
@login_required
def trades_tracker():
    current_date = datetime.date.today()

    user_trades = UserTrade.get_all(user_id=1)
    user_open_trades = []
    user_closed_trades = []

    initial_amount = User.get_amount(user_id=1)
    trade_labels = [0]
    trade_values = [initial_amount]

    current_contracts_number = 0
    winning_trades = 0
    losing_trades = 0
    total_return = 0
    trade_accuracy = 0

    for trade in user_trades:
        if trade.status == 'open':
            user_open_trades.append(trade)
            current_contracts_number += trade.position_size
        elif trade.status == 'closed':
            user_closed_trades.append(trade)
            print(trade)
            trade_value = trade.credit_to_open * trade.position_size - trade.credit_to_close * trade.position_size - trade.commission

            if trade_value > 0:
                winning_trades += 1
            else:
                losing_trades += 1

            trade_values.append(float(trade_values[-1]) + float(trade_value))
            trade_labels.append(trade_labels[-1] + 1)

    if user_closed_trades:
        trade_accuracy = winning_trades/len(user_closed_trades)*100

    total_return = trade_values[-1] - initial_amount

    stats = [
        {'label': 'Total Return', 'value': f"{'-' if total_return < 0 else ''}${abs(total_return)}"},
        {'label': 'Trade Accuracy', 'value': f"{trade_accuracy}%"},
        {'label': 'Total Open Trades', 'value': len(user_open_trades)},
        {'label': 'Total Closed Trades', 'value': len(user_closed_trades)},
        {'label': 'Current Contracts', 'value': f"{current_contracts_number}"},
        {'label': 'Max Contracts per Trade', 'value': f"{int(trade_values[-1]/10/200)}/{int(trade_values[-1]/200)}"},
        {'label': 'Total Winning Trades', 'value': winning_trades},
        {'label': 'Total Losing Trades', 'value': losing_trades},
    ]

    stocks = ['SPY', 'QQQ', 'DIA']
    stocks_data = {}

    for stock_symbol in stocks:
        live_price, _, _ = controller.get_chart_data(stock_symbol)
        stocks_data[stock_symbol] = round(live_price, 2)

    return render_template('trades_tracker.html', active_page='trades-tracker',
                           current_date=current_date, stats=stats, user_trades=user_trades, user_open_trades=user_open_trades, user_closed_trades=user_closed_trades, trade_labels=trade_labels,
                           trade_values=trade_values, stocks_data=stocks_data)


@app.route('/trades-backtest')
def trades_backtest():
    strategy_name = request.args.get('name') or 'Trend_Up'
    if 'name' not in request.args:
        return redirect(url_for('trades_backtest', name='Trend_Up'))

    current_date = datetime.date.today()

    trades = Trade.get_all(strategy=strategy_name.replace('_', ' '))
    filter_trades = []

    initial_amount = 0
    trade_labels = [0]
    trade_values = [initial_amount]

    winning_trades = 0
    losing_trades = 0
    total_return = 0

    for trade in trades:
        if trade.status == 'WIN':
            winning_trades += 1
            trade_values.append(float(trade_values[-1]) + float(trade.min_credit))
        elif trade.status == 'LOSE':
            losing_trades += 1
            trade_values.append(float(trade_values[-1]) - (150 - float(trade.min_credit)))
        else:
            continue

        filter_trades.append(trade)
        trade_labels.append(trade_labels[-1] + 1)

    if len(filter_trades) == 0:
        trade_accuracy = 0
    else:
        trade_accuracy = winning_trades / len(filter_trades) * 100

    total_return = trade_values[-1] - initial_amount
    time_period_days = (trades[0].date_alerted - trades[-1].date_alerted).days
    time_period_years = time_period_days / 365.0
    if time_period_years > 0 and trade_values[-1] > 0:
        annualized_return = ((trade_values[-1] / 1) ** (1 / time_period_years)) - 1
    else:
        annualized_return = 0  # Default value in case of division by zero or invalid input

    stats = [
        {'label': 'Total Return', 'value': f"{'-' if total_return < 0 else ''}${abs(total_return)}"},
        {'label': 'Annualized Return', 'value': f"{round(annualized_return,2)}%"},
        {'label': 'Trade Accuracy', 'value': f"{int(trade_accuracy)}%"},
        {'label': 'Total Closed Trades', 'value': len(filter_trades)},
        {'label': 'Total Winning Trades', 'value': winning_trades},
        {'label': 'Total Losing Trades', 'value': losing_trades},
    ]

    return render_template('trades_backtest.html', active_page='trades-backtest',
                           current_date=current_date, stats=stats, trades=filter_trades, trade_labels=trade_labels,
                           trade_values=trade_values)


@app.route('/chatbot', methods=['GET','POST'])
def chatbot():
    if request.method == 'GET':
        return render_template('chatbot.html', active_page='chatbot')

    user_message = request.json.get('userMessage')
    chat_history = request.json.get('chatHistory')

    result = controller.get_chatbot_response(user_message, chat_history)
    response = {'botResponse': result['answer']}

    return jsonify(response)




@app.route('/create', methods=['GET', 'POST'])
def create():
    ticker = request.form['ticker']

    if request.form['trade_type'] == 'put':
        trade_type = 'Put Credit Spread'
    else:
        trade_type = 'Cal Credit Spread'

    sold_strike_price = float(request.form['sold_strike_price'])
    credit_to_open = float(request.form['credit_to_open'])
    commission = float(request.form['commission'])
    position_size = int(request.form['position_size'])
    trade_open = request.form['trade_open_date']
    trade_expiration = request.form['trade_expiration_date']

    new_trade = UserTrade(user_id=1, ticker=ticker, trade_type=trade_type,
                          sold_strike_price=sold_strike_price, credit_to_open=credit_to_open, commission=commission,
                          position_size=position_size, trade_open_date=trade_open, trade_expiration_date=trade_expiration, status='open')

    new_trade.create()

    return redirect('/trades-tracker')


# Route to handle Close action
@app.route('/close', methods=['GET', 'POST'])
def close_action():
    trade_id = request.form['trade_id']
    credit_to_close = request.form['credit_to_close']
    commission = request.form['commission']
    trade_close_date = request.form['trade_close_date']
    UserTrade.close(trade_id, credit_to_close, commission, trade_close_date)

    return redirect('/trades-tracker')


# Route to handle Modify action
@app.route('/modify', methods=['GET', 'POST'])
def modify_action():
    trade_id = int(request.form['trade_id'])
    ticker = request.form['ticker']
    trade_type = request.form['trade_type']
    sold_strike_price = float(request.form['sold_strike_price'])
    position_size = int(request.form['position_size'])
    credit_to_open = float(request.form['credit_to_open'])
    commission = float(request.form['commission'])
    trade_open_date = request.form['trade_open_date']
    trade_expiration_date = request.form['trade_expiration_date']

    UserTrade.edit(trade_id, ticker, trade_type, sold_strike_price, position_size,
                       credit_to_open, commission, trade_open_date, trade_expiration_date)

    return redirect('/trades-tracker')

# Route to handle Clone action
@app.route('/clone', methods=['GET', 'POST'])
def clone_action():
    user_id = 1
    ticker = request.form['ticker']
    trade_type = request.form['trade_type']
    sold_strike_price = float(request.form['sold_strike_price'])
    position_size = int(request.form['position_size'])
    credit_to_open = float(request.form['credit_to_open'])
    commission = float(request.form['commission'])
    trade_open_date = request.form['trade_open_date']
    trade_expiration_date = request.form['trade_expiration_date']

    UserTrade.clone(user_id, ticker, trade_type, sold_strike_price, position_size,
                       credit_to_open, commission, trade_open_date, trade_expiration_date)

    return redirect('/trades-tracker')

# Route to handle Delete action
@app.route('/delete', methods=['GET', 'POST'])
def delete_action():
    trade_id = request.form['trade_id']
    UserTrade.delete(trade_id)

    return redirect('/trades-tracker')
