// ignore_for_file: avoid_unnecessary_containers

import 'dart:io';
import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'code.dart' as code;
import 'select_server.dart' as server;
import 'package:uuid/uuid.dart';

class HomePage extends StatefulWidget {
  const HomePage({Key? key}) : super(key: key);

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final ImagePicker imgpicker = ImagePicker();
  Future<XFile?>? file;
  String status = '';
  String base64Image = "";
  XFile? tmpFile;
  String errMessage = 'Error Uploading Image';
  static String uploadEndPoint = code.url;

  final objName = TextEditingController();
  String id = const Uuid().v1();

  @override
  void dispose() {
    objName.dispose();
    super.dispose();
  }

  setStatus(String message) {
    setState(() {
      status = message;
    });
  }

  chooseImage() {
    var xfile = (imgpicker.pickImage(source: ImageSource.gallery));
    setState(() {
      file = xfile;
    });
  }

  Widget showImage() {
    return FutureBuilder<XFile?>(
      future: file,
      builder: (BuildContext context, AsyncSnapshot<XFile?> snapshot) {
        if (snapshot.connectionState == ConnectionState.done &&
            null != snapshot.data) {
          tmpFile = snapshot.data;
          base64Image =
              base64Encode(File(snapshot.data!.path).readAsBytesSync());
          return Flexible(
            child: Column(children: [
              Image.file(
                File(snapshot.data!.path),
                fit: BoxFit.fill,
              ),
              TextField(
                controller: objName,
                decoration: const InputDecoration(
                  border: UnderlineInputBorder(),
                  labelText: "Enter The Object In The Image",
                ),
              )
            ]),
          );
        } else if (null != snapshot.error) {
          return Text(
            'Error Picking Image:  ${snapshot.error}',
            style: const TextStyle(color: Colors.white),
            textAlign: TextAlign.center,
          );
        } else {
          return const Text(
            'No Image Selected',
            style: TextStyle(color: Colors.white),
            textAlign: TextAlign.center,
          );
        }
      },
    );
  }

  startUpload() {
    if (objName.text.length <= 2) {
      const snackBar =
          SnackBar(content: Text('Please enter a valid object name.'));

      ScaffoldMessenger.of(context).showSnackBar(snackBar);
      return;
    }

    setStatus('Uploading Image...');
    if (null == tmpFile) {
      setStatus("$errMessage, tmpFile is null");
      return;
    }
    String fileName =
        "${objName.text}${tmpFile!.path.substring(tmpFile!.path.lastIndexOf("."))}";
    upload(fileName);
  }

  upload(String fileName) {
    if (kDebugMode) {
      print(base64Image.substring(0, 10));
    }
    http.post(Uri.parse(uploadEndPoint), body: {
      "image": base64Image,
      "name": fileName,
      "id": id
    }).then((result) {
      setStatus(result.statusCode == 200
          ? result.body
          : "$errMessage ${result.statusCode}");
    }).catchError((error) {
      setStatus(error.toString());
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color.fromARGB(255, 70, 70, 70),
      body: Container(
        padding: const EdgeInsets.all(30.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: <Widget>[
            ElevatedButton(
              onPressed: chooseImage,
              child: const Text('Choose Image'),
            ),
            const SizedBox(
              height: 20.0,
            ),
            showImage(),
            const SizedBox(
              height: 20.0,
            ),
            ElevatedButton(
              onPressed: startUpload,
              child: const Text('Upload Image'),
            ),
            const SizedBox(
              height: 20.0,
            ),
            Text(
              status,
              textAlign: TextAlign.center,
              style: const TextStyle(
                color: Colors.green,
                fontWeight: FontWeight.w500,
                fontSize: 20.0,
              ),
            ),
            const SizedBox(
              height: 20.0,
            ),
            Container(
                alignment: Alignment.bottomCenter,
                child: ElevatedButton(
                  child: const Text("<- Back"),
                  onPressed: () {
                    code.back = true;
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                          builder: (context) => const server.SelectServer()),
                    );
                  },
                ))
          ],
        ),
      ),
    );
  }
}
