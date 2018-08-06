from masternode_modules.chunk_manager import ChunkManager
from masternode_modules.masternode import MasterNodeManager
from masternode_modules.settings import MasterNodeSettings

BASEDIR = "/home/synapse/tmp/animecoin/tmpstorage"
CHUNK_LIST = [
    "f03214550836c2a5c576a42e7522e3c844fa949dfd03456aa28d22fcc5832746",
    "9d79bb2f78a6e9f06cfb74715d30fde0ee863396be87c45a53eee9942f726d02",
    "d285f30e18eeeaaa2ca51b632478c9ce8a564e3e414142982ddda846dcb671be",
    "fd55893d6e255877f811d83009925c2bf8f34b6e207099a4bbd5ea09e358bb37",
    "b97b4fa39bd3ae847b32840131b9a604b259582531beae3bf38c686df48db797",
    "9461e71bf28af1f6d77a20a28d7ef98a04a0650a9a4e195c54523586c9404683",
    "2fcf07e9f15904b7aa4ac9c143b58e1aeb42b398b8d480c9bf0462bae880c348",
    "9335fa391063f0d1d3711b604169f05469d70da0711232d5447c165907562fc9",
    "326628203ec523a74280a4ca70b7f13ef6402688c91ff0f6189988336b74db8f",
    "0d88fa906bdd47a82d8fa3c90103519e40049204728730bce30bbbf97fd9622b",
    "b88f80328aa873fe3a753b929777baa6f7148dc3a8d6dfe658a29af63aa93482",
    "6426a958221015977492baa94ffa8a8ec501ec5143ea06e4f674f0929351aa7c",
    "caa2a70081629efff885dc7f200d2713558015108b65b862df684ad0669fc214",
    "53d9f001bddac038812029a4496253536d9af56136fe5ca27b0899292a4e8b82",
    "c78dff059f505b5a40178724af3e86f40a4da0892120d6bf14cc5f7aec1ad2ae",
    "1a0246daad1690ec27498dc7a43271a6be723d63cbdb587d73d19b43ccb94aad",
    "8bc31d1b9f34e4572eef75eec61a83b4710638ebbad1b3dab10774e178760b9f",
    "18c2a9c8d660d465f5dff4980ad61261e1b16fcca4bc1f7444b33c451b92a85d",
    "18fdcd377d97f452eb1890bca154b8429c78db439c7a340dcd1819a51e6f1ae6",
    "72694713863f5ab6d9c8253d5341f91daca3d744b18077c80b701ecd3060c1b6",
    "41342014dcd45f984b1bd59fe12270a731a623c5aa23c1306ae03b2fd25563b1",
    "ce25c51164ad3c216e31d977aa7aff8313e51f64f5c5392af22e26fa3ea848ca",
    "4551c9b8e3bfbd985c3eb782e0bd9e3b95202b1af76241df864317a115662aaf",
    "f1e891235ca0ea5389baec4e62069b1234066d3f26b1481e4a7d8ae3ecbe0937",
    "bdfadf20ec3c9f5f4edee410914a6c503f140343975552cc9eaf13e4086789ee",
    "30270ce7b6f8b06e862a595665816ce0703cb66eda302bf9a9ed98505e9ee014",
    "3fa667a770fee088d925fc863002c8e2aad3b59213163db460bcc75aeb11ff6e",
    "bec655ec713fc852d6b5602100375602861afb86cac0a8a835a66ed7d08066e1",
    "e6e4e9e8d21ffa918dbe579689a4391d9943193936fcf9d91b03c65895ead46b",
    "0b11be772f254b21b76f55ce27fbb61dd24eddf7eb89bc7d2a8178e6f7d8b7c6",
    "05b401ec3928bf8483542f6489c3925df6bb655e4adcb03d3906f75da1c9c254",
    "31fafb7bc2ccd2e7745cc84d273fcfcf09ffe47f745ccc8f00ff2c9b27d3d4fe",
    "f4626324108e717f72aaece63f1f1fd45e37d29f4d0c2e4fad2693e9e456aa6a",
    "529ba85207ce752e5f0b81ff07a57752e8735dba6650a04f9b0777a198e0a55e",
    "ab2c73ee3748ea4b807cb36cea3e7234ffb924217a529729e44746beeff80c16",
    "9f9b98a4316896e0ff581a31731445540dce67ab9f2630d9d4568a1935e4ed65",
    "40583ea2d8a99facc55e6ea9fcb28c1efacd373fd04284f64dac48e555592552",
    "fc3bf08be983271c1b4dd18ca020ca8d58a11a4b7d0bc2579ad6b6e0498c060e",
    "14c89657c4c2647a3092d17d6942a5cafd77ea63b5e381b4f28bda19cce9fce0",
    "b91b5d0d57caf7d1cc5eefe7859c8c46eca2a8b72f84b3173994b42d38cfe72e",
    "21d58eb34b7c048ce326a9e98a44f2e65259245299622b878eb98549b46d7707",
    "f59dc1bedf9c80156253d80c70f3c7b66d6709d0b373dc1c53477ac38d3cf7bb",
    "02e2719070e2eb9d1ddeba0462331a62f2f7b17faa8f1f861fd56fec3f1bc32d",
    "ab35bd3a7649c41de999dc81269aa886e70b74ae03838127c36aa6cb056e62a9",
    "67f7c29e9a29c37b330fb031aa1a177d7a312b22b9c0a4bcd33702b22374bf27",
    "9720d9e482794cb56be83ffd2840756ac10a927cbfe08ef3b06d1fce06dcee56",
    "dcc22f6efe0a657c511f4c83970b544127f1dc67657bbbea6b7f1f5f3228db78",
    "f2ca751fe881cc2ddc2d999e070083d8576cc57f662ec93b266f797ec3fd17f5",
    "90aab23e4f5b6802573e0816b8416b936fae51f39a9d8c3a3979dba840236342",
    "99bd2ddd99cd59569c68520dfa25cd92b5618de7c3897007bbc83f0951083b7a",
    "0b80da0f5574251e2d569b61135f08a257c5de53338fee6b6e18e98914d07c79",
    "bcce66a5d2969c10182ccd2eed30e12c2fcd498ee03a9e9b0d3e4ea7f0cdf05f",
    "f90b1bea24e612811a7cbb8ab3eea5fe1f8af5d4bca2d929b881d35e15363f23",
    "b0b7aa2be9f7b8419bc76655f08299f5d2c22a02783b5ed75f4be6c5ef61bcdd",
    "3d228f4baeef9c7d24a00ab441a8c33317bce5fe5055d34504377051bc0a5132",
    "8c712f41e52bdde9251c0e80e249066b25f53b6358d624a459d07b88bc1d10fb",
    "e4feb67f03ed5436c0acb548f4f889eae53f08789b521bb0b6ad46ea6a85d7f0",
    "585cdc199aab54060fca98646cd780fbf0b7f0a7a049ad3e0a929709ed155b68",
    "7035a6039925f2275342ecb276850ba70084ee66a2c05b00520dfdf1063c2142",
    "7f40d03ab3682e758f45f4e5cc4705b4bc2bd85171f816ee976e49a873aa427f",
    "b709c6274bee43f6745cd3c25f333c88665bd43b4d483c19ee95c8a3e7630ad6",
    "a54da47855defeb2cb2c8995a24c5c016e536347b98293a29bfd73f90bddd093",
    "dd52953e6340347f1936c0329a9f3e119ef70e2eff73d341a736b852175180b4",
    "6219b6de1d7945b69e470a523cc92d01f54696353561c2dfe24cfcf89c9790f9",
    "258f2c0037d2cbba41bdf590a709c8c5d02a2960c9df5c1b59d1d4758a5d08a0",
    "85734d719fe7e9b5b7daceff5d412a6c5fca8e59c35cb57520090a22efe17ef9",
    "5572091ca40844cf3633ee26d7dc20ab27caded67faff566a9ef17fb7dadc34c",
    "609447cc4f0ae2a945f5daa6fb55bb3db1670d215de7c668abb6b5ea71449bb3",
    "e68f51eaadeef4f8d9261cd69be2bbf0dbee5ef3ba1a1c05119725c2bbfe17d0",
    "2c99bb9142be5e8c8a24c13fb01ed2b729a05850184fb9c206096f783691e730",
    "2316719feeabdb86558c4e6c0c94e1d37eb09110c63be0485f66ec855f675444",
    "ac5f93ef564221746b2b9568e841edae040a6482b5da3b6fe97181fde7d6a366",
    "fc7415b2faa4f08680a6e855ea6761c7a7a20a6d59167be372ff0657b6efce74",
    "74d22afaa5a0f096de8ae6eeb534438674bc6497611af122967457a280af27ac",
    "8113a79045c32a26f0fa636c1d3decbd611efe6804b601157dac1353d6892995",
    "000672b732f5c9aaa5026ca5b9efaf106968ad81486a4c6c0c900dadb684bcb0",
    "5eb86b69dbd66cb3235ac3a7f82e5f19ac5313e444f8a73c5df42f30440a1a30",
    "9281dffd2200d59dfd8a97992a6f1859b6b2300ef307b022f9ee52ebf4fad027",
    "420d7bad0d6400a4289b24a47690314db295a0e26d7f44a07ccb030c368aaae6",
    "6930e0877c4f726b146023b8e62beaf756a4befdd0071d9ad1260d379f91ce63",
    "1f12bda0fdadeb47f51f534a9b1df098fdb52b79154f72883ca9418a17318df4",
    "ae05329cffaec468a8ebfcb075e1e99b80016a1be04ef857d0c488c1c0e46989",
    "55fec495e8c4c4661e52fa80eeee0d41bccc1ca54c9e67334496db6a966ebe92",
    "90f7de19de3de13cecf78ffbdd4cbdd373d2d5f86977085b1bf11ee02501fde1",
    "d7042ea5e46dc5cf8f0ec4f04db6eabe021aba0d23a3a1cb1fb2e27fe81f9d89",
    "e1b7cd8771804b98ea50642d0f05cb21000c238e5dc7725073667edcb1a900e3",
    "9c97cc48f95c183c7ee4a5bafeca8ca6e3200f2d2634ce8283efb47f462b47cf",
    "d559a3e677bbe9a8acad169e889df8e15db103180c4a56a6d506c0b3d47d39c8",
    "68640ffbaac664d5c6bfd70c7766c8bd83d4de94d1ace3d5a5fb0540bdd419b1",
    "b050b299b55b31ea51494afa619339677cb323bd2e60a51898222555a99da6ed",
    "798658ae8610dfcd55e1d6fa889210971362e0a2c4fbd9926c0d0c55f04b0b5a",
    "de38dc6085835041d13387600710e34c081d6b9632f98bd8c8af167c2f1ad56b",
    "b27a20ae97ae3f8ce6fb9204d59a4c66aa19c0084942308704c36918e4fae743",
    "256c529487687e6dd7efb0e2f600c403af53f327a44eaa34acd2159094c3666d",
    "549af3f5e13df3352093b3e23eed4f7e18b74133bf74eb936e4fa5acae290c56",
    "6001796601758148be27d1c6d4f8c1a27e1cc5c9a99c4e684a3f8e05d3c87fc3",
    "6f1edb6bf795e0608ab9a82a6fd50f2ab2b1c9355907ea7d420f0d881cb640a9",
    "091c2c4335b6c27c892904b1acb252856bc247426b613ff0b5be9d21bff48070",
    "65821669f7add69a049a5c70f09fa58d21bfb26be873590870f640fffda79eda",
    "ba46617f21d6129599546811203175cbdab83122bb0b39017aa78b5baacbd379",
    "1a42debcb901ef1db8aaac7c3032aaf0e87c849b73fe00fc04b762375f14ec8e",
    "d9861816861dab20a41edddbbbd2e8d319dc3120b56de4614eb042243d553ccf",
    "2d286e7f8d072302231cf69e79077b886f939351d1fa1d47713103d80f66329c",
    "d95961d497e8a798143350116c5bfa67d8e9af4c5265ae8bc8a9b3bf07c07aff",
    "454056d170f6f8f9818f15af7a10b7123dd69f3b4dafaac7b6c92338cf0d1bc1",
]

MASTERNODES = [
    ("e0ede7e4685350241b090982b81421f63a86de2c8a7ad15711414984dda4c433", "127.0.0.1", "86752", None),
    ("3cde740fe1b77084c7440db1d9863105646b792ebc0ca8d5b21e21c46f6216e1", "127.0.0.1", "86753", None),
    ("ede8bcce0703a1e31bf503ea5e43226295b410ef45ef4706b4c5ffba62210767", "127.0.0.1", "86754", None),
]


if __name__ == "__main__":
    masternode_settings = MasterNodeSettings(basedir=BASEDIR, replication_factor=1)
    x = ChunkManager(MASTERNODES[0][0], masternode_settings, CHUNK_LIST, MASTERNODES[0:1])
    x.update_mn_list(MASTERNODES)
    x.new_chunks_added_to_blockchain(["42ad07fac0678fa2bac61b0255646ec960dee1bf2b646c88c07fb791c365d3a3"])
