def test_pool_token(w3, pool_token):
        assert pool_token.caller.decimals() == 18
