import 'dart:math';

import 'package:flutter/foundation.dart';
import 'package:photospin/home.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'code.dart' as code;
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

String _generateRandomString(int len) {
  var r = Random();
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  return List.generate(len, (index) => chars[r.nextInt(chars.length)]).join();
}

class SelectServer extends StatefulWidget {
  const SelectServer({Key? key}) : super(key: key);

  @override
  State<SelectServer> createState() => _SelectServerState();
}

class _SelectServerState extends State<SelectServer> {
  final gameCode = TextEditingController();
  String myCode = "";

  static const String uploadEndPoint = 'http://192.168.1.167:1024';

  _read(String key) async {
    final prefs = await SharedPreferences.getInstance();
    final value = prefs.getString(key) ?? "";
    if (kDebugMode) {
      print('read: $value');
    }
    return value;
  }

  _save(String key, String value) async {
    final prefs = await SharedPreferences.getInstance();
    prefs.setString(key, value);
    if (kDebugMode) {
      print('saved $value');
    }
  }

  @override
  void dispose() {
    gameCode.dispose();
    super.dispose();
  }

  _getKey() async {
    if (await _read("0") == "") {
      await _save("0", _generateRandomString(3));
    }
    myCode = await _read("0");
  }

  gamePost(String forum, String gameCodeGame) {
    http.post(Uri.parse(uploadEndPoint), body: {
      forum: gameCodeGame,
    }).then((result) {
      if (kDebugMode) {
        print(result.statusCode);
      }
      if (result.statusCode == 200 && result.body != "") {
        code.url = result.body;

        if (kDebugMode) {
          print(result.body);
        }
        http.get(Uri.parse(code.url));

        Navigator.push(
          context,
          MaterialPageRoute(builder: (context) => const HomePage()),
        );
      }
    });
  }

  join() {
    String gameCodeGame = gameCode.text;
    if (gameCode.text.length != 3) {
      const snackBar =
          SnackBar(content: Text('Please enter a valid game code.'));

      ScaffoldMessenger.of(context).showSnackBar(snackBar);
      return;
    }
    if (kDebugMode) {
      print("Beginning POST...");
      print(gameCodeGame);
    }

    gamePost("join", gameCodeGame);

    if (kDebugMode) {
      print("Finished POST!");
    }
  }

  //create game
  create() async {
    await _getKey();
    if (kDebugMode) {
      print("Beginning POST...");
      print(myCode);
    }
    gamePost("create", myCode);
    if (kDebugMode) {
      print("Finished POST!");
    }
  }

  //garbage server
  garbage() async {
    await _getKey();
    print("garbage called");
    if (kDebugMode) {
      print("Beginning POST...");
      print(myCode);
    }

    gamePost("destroy", myCode);

    if (kDebugMode) {
      print("Finished POST!");
    }
  }

  @override
  Widget build(BuildContext context) {
    if (code.back) {
      code.back = false;
      garbage(); //destroy server
    }
    return Scaffold(
      body: Container(
        width: double.infinity,
        height: double.infinity,
        alignment: Alignment.bottomCenter,
        child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              ElevatedButton(
                  onPressed: create, child: const Text("Create Game")),
              const SizedBox(
                height: 20.0,
              ),
              TextField(
                textCapitalization: TextCapitalization.characters,
                controller: gameCode,
                decoration: const InputDecoration(
                  border: UnderlineInputBorder(),
                  labelText: "Enter A Valid Game Code",
                ),
              ),
              const SizedBox(
                height: 20.0,
              ),
              ElevatedButton(
                  onPressed: join, child: const Text("Connect to Server!")),
            ]),
      ),
    );
  }
}
