# MOL LibraExplorer
An Explorer for the Libra Blockchain Netwrok powered by `MoveOnLibra` OpenAPI. The `MoveOnLibra` is an OpenAPI platform which make write Libra wallet and smart contract program easier.

## A Realtime Libra Blockchain Explorer
There are several Libra explorers there already. Why write another Libra Explorer? Because all other explorers there are not realtime. They pull data from Libra blockchian and save it to their own private database. When you access their explorer website, they search data from private database and return data to you.

On the other hand, `MOL LibraExplorer` fetch data from original Libra blockchain in realtime and return data to you. So, the data is more accurate and fresher. You can access the Libra blockchain data by visiting following website:

[explorer.moveonlibra.com](http://explorer.moveonlibra.com/) which is power by this opensource project.

It's fast and accurate.


## Support Third-party Libra Network
"MOL LibraExplorer" can support any third-party Libra network as long as the host and port of those network is publicly accessible. The easiest way to browser a third-party libra network is prefix the host and port to "explorer.moveonlibra.com" with following syntax:

 ```plaintext
 http://<host>-<port>.explorer.moveonlibra.com/
 ```
for example, There is a libra-swarm network started by run:

 ```sh
 cargo run -p libra-swarm
 ```
and the host and port are "47.254.29.109" and "36765" respectively. So you can brower the blockchain data on this network by open this url:

http://47.254.29.109-36765.explorer.moveonlibra.com/

We will add more formal method to support third-party Libra network. Currently, you cann't mint coin and commit transactions on these third-party Libra network explorer.

## Feedback is welcome.

TODO: multi-language support
