Deploy Emergency DAO through Aragon UI - Membership template

After making DAO - assigning `MINT_ROLE` and `BURN_ROLE` to deployer address in order to add initial members faster 

After adding initial members, `MINT_ROLE` and `BURN_ROLE` manager will be assigned to Emergency Voting and managed by Ownership Agent in main DAO
and the `APP_MANAGER_ROLE` and `CREATE_PERMISSIONS_ROLE` should be set to Ownership Agent

[Install Aragon CLI](https://github.com/aragon/aragon-cli)
Preferably, for easier usage, install [frame.sh](https://frame.sh/)

`dao new --use-frame --env aragon:rinkeby`

Ownership Agent: `dao install $DAO_ADDRESS agent --use-frame --env aragon:rinkeby`

Parameter Agent: `dao install $DAO_ADDRESS agent --use-frame --env aragon:rinkeby`

Vault Agent: `dao install $DAO_ADDRESS agent --use-frame --env aragon:rinkeby`

Ownership Voting: `dao install $DAO_ADDRESS curve-voting6.open.aragonpm.eth --app-init-args $VOTING_ESCROW 510000000000000000 500000000000000000 3600 2500 10 2500 50000 10 1000 --use-frame --env aragon:rinkeby`

Parameter Voting: `dao install $DAO_ADDRESS curve-voting6.open.aragonpm.eth --app-init-args $VOTING_ESCROW 700000000000000000 150000000000000000 3600 2500 10 2500 50000 10 1000 --use-frame --env aragon:rinkeby`

`dao acl create $DAO_ADDRESS $OWNERSHIP_VOTING_APP_ADDRESS CREATE_VOTES_ROLE 0xffffffffffffffffffffffffffffffffffffffff $OWNERSHIP_VOTING_APP_ADDRESS --use-frame --env aragon:rinkeby`

`dao acl create $DAO_ADDRESS $PARAMETER_VOTING_APP_ADDRESS CREATE_VOTES_ROLE 0xffffffffffffffffffffffffffffffffffffffff $PARAMETER_VOTING_APP_ADDRESS --use-frame --env aragon:rinkeby`

`dao acl create $DAO_ADDRESS $OWNERSHIP_AGENT_ADDRESS EXECUTE_ROLE $OWNERSHIP_VOTING_APP_ADDRESS $OWNERSHIP_VOTING_APP_ADDRESS --use-frame --env aragon:rinkeby`

`dao acl create $DAO_ADDRESS $PARAMETER_AGENT_ADDRESS EXECUTE_ROLE $PARAMETER_VOTING_APP_ADDRESS $PARAMETER_VOTING_APP_ADDRESS --use-frame --env aragon:rinkeby`

`dao acl create $DAO_ADDRESS $OWNERSHIP_VOTING_APP_ADDRESS ENABLE_VOTE_CREATION $EMERGENCY_AGENT_ADDRESS $EMERGENCY_AGENT_ADDRESS --use-frame --env aragon:rinkeby`

`dao acl create $DAO_ADDRESS $PARAMETER_VOTING_APP_ADDRESS ENABLE_VOTE_CREATION $EMERGENCY_AGENT_ADDRESS $EMERGENCY_AGENT_ADDRESS --use-frame --env aragon:rinkeby`

`dao acl create $DAO_ADDRESS $OWNERSHIP_VOTING_APP_ADDRESS DISABLE_VOTE_CREATION $EMERGENCY_AGENT_ADDRESS $EMERGENCY_AGENT_ADDRESS --use-frame --env aragon:rinkeby`

`dao acl create $DAO_ADDRESS $PARAMETER_VOTING_APP_ADDRESS DISABLE_VOTE_CREATION $EMERGENCY_AGENT_ADDRESS $EMERGENCY_AGENT_ADDRESS --use-frame --env aragon:rinkeby`

`dao acl create $DAO_ADDRESS $OWNERSHIP_VOTING_APP_ADDRESS MODIFY_SUPPORT_ROLE $OWNERSHIP_VOTING_APP_ADDRESS $OWNERSHIP_VOTING_APP_ADDRESS --use-frame --env aragon:rinkeby`

`dao acl create $DAO_ADDRESS $OWNERSHIP_VOTING_APP_ADDRESS MODIFY_QUORUM_ROLE $OWNERSHIP_VOTING_APP_ADDRESS $OWNERSHIP_VOTING_APP_ADDRESS --use-frame --env aragon:rinkeby`

`dao acl create $DAO_ADDRESS $OWNERSHIP_VOTING_APP_ADDRESS SET_MIN_BALANCE_ROLE $OWNERSHIP_VOTING_APP_ADDRESS $OWNERSHIP_VOTING_APP_ADDRESS --use-frame --env aragon:rinkeby`

`dao acl create $DAO_ADDRESS $OWNERSHIP_VOTING_APP_ADDRESS SET_MIN_TIME_ROLE $OWNERSHIP_VOTING_APP_ADDRESS $OWNERSHIP_VOTING_APP_ADDRESS --use-frame --env aragon:rinkeby`

`dao acl create $DAO_ADDRESS $PARAMETER_VOTING_APP_ADDRESS MODIFY_SUPPORT_ROLE $PARAMETER_VOTING_APP_ADDRESS $PARAMETER_VOTING_APP_ADDRESS --use-frame --env aragon:rinkeby`

`dao acl create $DAO_ADDRESS $PARAMETER_VOTING_APP_ADDRESS MODIFY_QUORUM_ROLE $PARAMETER_VOTING_APP_ADDRESS $PARAMETER_VOTING_APP_ADDRESS --use-frame --env aragon:rinkeby`

`dao acl create $DAO_ADDRESS $PARAMETER_VOTING_APP_ADDRESS SET_MIN_BALANCE_ROLE $PARAMETER_VOTING_APP_ADDRESS $PARAMETER_VOTING_APP_ADDRESS --use-frame --env aragon:rinkeby`

`dao acl create $DAO_ADDRESS $PARAMETER_VOTING_APP_ADDRESS SET_MIN_TIME_ROLE $PARAMETER_VOTING_APP_ADDRESS $PARAMETER_VOTING_APP_ADDRESS --use-frame --env aragon:rinkeby`

`dao acl create $DAO_ADDRESS $VAULT_AGENT_ADDRESS TRANSFER_ROLE $OWNERSHIP_VOTING_APP_ADDRESS $OWNERSHIP_VOTING_APP_ADDRESS --use-frame --env aragon:rinkeby`

# And to give up control to main DAO in the end - 

In both main DAO and Emergency DAO change system permissions(`APP_MANAGER_ROLE`, `CREATE_PERMISSIONS_ROLE`, ...) to Ownership Voting App

[Tutorial](https://help.aragon.org/article/21-permissions)

`dao acl create $DAO_ADDRESS $DAO_ADDRESS APP_MANAGER_ROLE $OWNERSHIP_VOTING_APP_ADDRESS $OWNERSHIP_VOTING_APP_ADDRESS --use-frame --env aragon:rinkeby`

`dao acl create $DAO_ADDRESS $DAO_ACL_ADDRESS CREATE_PERMISSIONS_ROLE $OWNERSHIP_VOTING_APP_ADDRESS $OWNERSHIP_AGENT_ADDRESS --use-frame --env aragon:rinkeby`


`dao acl create $DAO_ADDRESS $OWNERSHIP_VOTING_APP_ADDRESS DISABLE_VOTE_CREATION 0x0000000000000000000000000000000000000000 0x0000000000000000000000000000000000000000 --use-frame --env aragon:rinkeby`

`dao acl create $DAO_ADDRESS $PARAMETER_VOTING_APP_ADDRESS DISABLE_VOTE_CREATION 0x0000000000000000000000000000000000000000 0x0000000000000000000000000000000000000000 --use-frame --env aragon:rinkeby`

When verified that all is good, can proceed to deploy on mainnet by changing `--env aragon:rinkeby` to `--env aragon:mainnet`