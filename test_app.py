import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from app import create_app
from models import setup_db, Strategy, Bot

# Preventing random test order

unittest.TestLoader.sortTestMethodsUsing = None

# Building up test case

class TradingBotsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.database_name = "capstone"
        self.database_path = "postgresql://{}/{}".format(
            'rj@localhost',
            self.database_name
        )
        setup_db(self.app, self.database_path)

        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            self.db.create_all()

    def tearDown(self):
        pass

    # Test greeting message

    def test_get_greeting(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)

    # Begin strategies endpoints test

    # Get public strategies

    def test_get_public_strategies(self):
        res = self.client.get('/strategies')
        self.assertEqual(res.status_code, 200)

    # Get non-public strategies without token

    def test_get_non_public_strategies(self):
        res = self.client.get('/strategies-detail')
        self.assertEqual(res.status_code, 401)

    # Get non-public strategies with Trader token

    def test_get_strat_detail_trader(self):
        res = self.client.get(
            '/strategies-detail',
            headers={
                "Authorization": f"Bearer {os.getenv('TRADER')}"
            }
        )
        self.assertEqual(res.status_code, 200)

    # Get non-public strategies with Quant Manager token

    def test_get_strat_detail_quant(self):
        res = self.client.get(
            '/strategies-detail',
            headers={
                "Authorization": f"Bearer {os.getenv('QUANT_MANAGER')}"
            }
        )
        self.assertEqual(res.status_code, 200)

    # Add strategy without permission

    def test_post_strategy_trader(self):
        res = self.client.post(
            '/strategies/create',
            json={
                "id": 69,
                "name": "New Strategy",
                "params": "candles, signal"
            },
            headers={
                "Authorization": f"Bearer {os.getenv('TRADER')}"
            }
        )
        self.assertEqual(res.status_code, 401)

    # Add strategy with permission

    def test_post_strategy_quant(self):
        res = self.client.post(
            '/strategies/create',
            json={
                "id": 69,
                "name": "New Strategy",
                "params": "candles, signal"
            },
            headers={
                "Authorization": f"Bearer {os.getenv('QUANT_MANAGER')}"
            }
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])

    # Bad request

    def test_unprocessable(self):
        res = self.client.post(
            '/strategies/create',
            json={
                "name": "Oh no",
                "age": "string"
            },
            headers={
                "Authorization": f"Bearer {os.getenv('QUANT_MANAGER')}",
            }
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])

    # Patch strategy info without permission

    def test_patch_strategy_no_auth(self):
        res = self.client.patch(
            '/strategies/1',
            json={
                "name": "string"
            },
            headers={
                "Authorization": f"Bearer {os.getenv('TRADER')}"
            }
        )
        self.assertEqual(res.status_code, 401)

    # Patch strategy with permission

    def test_patch_strat_auth(self):
        res = self.client.patch(
            '/strategies/1',
            json={
                "name": "Donchian Strategy",
                "params": "channel, reference"
            },
            headers={
                "Authorization": f"Bearer {os.getenv('QUANT_MANAGER')}",
            }
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    # Delete strategy without permission

    def test_del_strategy_no_auth(self):
        res = self.client.delete(
            '/strategies/69',
            headers={
                "Authorization": f"Bearer {os.getenv('TRADER')}"
            }
        )
        self.assertEqual(res.status_code, 401)

    # Delete strategy with permission

    def test_del_strategy_auth(self):
        res = self.client.delete(
            '/strategies/69',
            headers={
                "Authorization": f"Bearer {os.getenv('QUANT_MANAGER')}"
            }
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])



    # Begin Bot endpoints test

    # Get public bots

    def test_get_public_bots(self):
        res = self.client.get('/bots')
        self.assertEqual(res.status_code, 200)

    # Get non-public bots without token

    def test_get_non_public_bots(self):
        res = self.client.get('/bots-detail')
        self.assertEqual(res.status_code, 401)

    # Get non-public bots with Trader token

    def test_get_bot_detail_trader(self):
        res = self.client.get(
            '/bots-detail',
            headers={
                "Authorization": f"Bearer {os.getenv('TRADER')}"
            }
        )
        self.assertEqual(res.status_code, 200)

    # Get non-public bots with Quant Manager token

    def test_get_bot_detail_quant(self):
        res = self.client.get(
            '/bots-detail',
            headers={
                "Authorization": f"Bearer {os.getenv('QUANT_MANAGER')}"
            }
        )
        self.assertEqual(res.status_code, 200)

    # Add bots without permission

    def test_post_bot_trader(self):
        res = self.client.post(
            '/bots/create',
            json={
                "id": 69,
                "name": "New Bot",
            },
            headers={
                "Authorization": f"Bearer {os.getenv('TRADER')}"
            }
        )
        self.assertEqual(res.status_code, 401)

    # Add bot with permission

    def test_bot_post_quant(self):
        res = self.client.post(
            '/bots/create',
            json={
                "id": 69,
                "name": "New Bot",
                "active": True,
                'strategy_id' : 1,
                'timeframe' : "1h",
                'param_values' : "7,price",                
            },
            headers={
                "Authorization": f"Bearer {os.getenv('QUANT_MANAGER')}"
            }
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])

    # Bad request

    def test_unprocessable_bot(self):
        res = self.client.post(
            '/bots/create',
            json={
                "name": "Oh no",
                "age": "string"
            },
            headers={
                "Authorization": f"Bearer {os.getenv('QUANT_MANAGER')}",
            }
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])

    # Patch bot info without permission

    def test_patch_bot_no_auth(self):
        res = self.client.patch(
            '/bots/1',
            json={
                "name": "string"
            }
        )
        self.assertEqual(res.status_code, 401)

    # Patch bot with permission

    def test_patch_bot_auth(self):
        res = self.client.patch(
            '/bots/1',
            json={
                "name": "Great Bot!"
            },
            headers={
                "Authorization": f"Bearer {os.getenv('TRADER')}",
            }
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    # Delete bot without permission

    def test_del_bots_no_auth(self):
        res = self.client.delete(
            '/bots/69',
            headers={
                "Authorization": f"Bearer {os.getenv('TRADER')}"
            }
        )
        self.assertEqual(res.status_code, 401)

    # Delete bot with permission

    def test_del_bots_auth(self):
        res = self.client.delete(
            '/bots/69',
            headers={
                "Authorization": f"Bearer {os.getenv('QUANT_MANAGER')}"
            }
        )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])


if __name__ == "__main__":
    unittest.main()
