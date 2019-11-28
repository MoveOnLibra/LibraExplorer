
## Support Third-party Libra Network
"MOL LibraExplorer" can support any third-party Libra network as long as the host and port of those network is publicly accessible. The easiest way to browser a third-party libra network is prefix the host and port to "explorer.moveonlibra.com" with following syntax:

 ```plaintext
 http://<host>-<port>.explorer.moveonlibra.com/
 ```
for example, There is a libra-swarm network started by run:

 ```sh
 cargo run -p libra-swarm
 ```
and the host and port are "47.254.29.109" and "33333" respectively. So you can brower the blockchain data on this network by open this url:

http://47.254.29.109-33333.explorer.moveonlibra.com/

We will add more formal method to support third-party Libra network. Currently, you cann't mint coin and commit transactions on these third-party Libra network explorer.

