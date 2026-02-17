import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:io';
import 'package:image_picker/image_picker.dart';

void main() {
  runApp(const PesticideSprinklerApp());
}

class PesticideSprinklerApp extends StatelessWidget {
  const PesticideSprinklerApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Smart Pesticide Sprinkler',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primarySwatch: Colors.green,
        scaffoldBackgroundColor: Colors.grey[100],
      ),
      home: const DashboardScreen(),
    );
  }
}

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({Key? key}) : super(key: key);

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  // Backend API URL - Update with your server IP
  final String apiUrl = 'http://192.168.1.100:5000';
  
  // Sensor data
  Map<String, dynamic> sensorData = {
    'temperature': 0.0,
    'humidity': 0.0,
    'soil_moisture': 0.0,
  };
  
  bool isLoading = false;
  String statusMessage = 'Ready';

  @override
  void initState() {
    super.initState();
    fetchSensorData();
  }

  Future<void> fetchSensorData() async {
    setState(() => isLoading = true);
    
    try {
      final response = await http.get(Uri.parse('$apiUrl/sensors'));
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          sensorData = data['data'];
          statusMessage = 'Connected';
        });
      } else {
        setState(() => statusMessage = 'Connection failed');
      }
    } catch (e) {
      setState(() => statusMessage = 'Error: $e');
    } finally {
      setState(() => isLoading = false);
    }
  }

  Future<void> checkConditions() async {
    setState(() => isLoading = true);
    await fetchSensorData();
    
    final moisture = sensorData['soil_moisture'] ?? 0;
    bool safe = moisture >= 40 && moisture <= 70;
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(safe ? '✅ Safe to Spray' : '⚠️ Not Safe'),
        content: Text(
          safe
              ? 'Soil moisture is $moisture%. Conditions are safe for spraying.'
              : 'Soil moisture is $moisture%. Safe range is 40-70%.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('OK'),
          ),
        ],
      ),
    );
    
    setState(() => isLoading = false);
  }

  Future<void> controlSpray(String command) async {
    setState(() => isLoading = true);
    
    try {
      final response = await http.post(
        Uri.parse('$apiUrl/control/spray'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'command': command,
          'soil_moisture': sensorData['soil_moisture'] ?? 50,
        }),
      );
      
      final data = json.decode(response.body);
      
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: Text(data['success'] ? '✅ Success' : '❌ Failed'),
          content: Text(data['message'] ?? data['reason'] ?? 'Unknown response'),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('OK'),
            ),
          ],
        ),
      );
    } catch (e) {
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('Error'),
          content: Text('Failed to send command: $e'),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('OK'),
            ),
          ],
        ),
      );
    } finally {
      setState(() => isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('🌱 Smart Sprinkler'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: fetchSensorData,
          ),
        ],
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: fetchSensorData,
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // Status Card
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          children: [
                            const Icon(Icons.wifi, size: 48, color: Colors.green),
                            const SizedBox(height: 8),
                            Text(
                              'Status: $statusMessage',
                              style: const TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    
                    const SizedBox(height: 16),
                    
                    // Sensor Data Grid
                    GridView.count(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      crossAxisCount: 2,
                      crossAxisSpacing: 16,
                      mainAxisSpacing: 16,
                      children: [
                        _buildSensorCard(
                          'Temperature',
                          '${sensorData['temperature']?.toStringAsFixed(1) ?? '--'}°C',
                          Icons.thermostat,
                          Colors.orange,
                        ),
                        _buildSensorCard(
                          'Humidity',
                          '${sensorData['humidity']?.toStringAsFixed(1) ?? '--'}%',
                          Icons.water_drop,
                          Colors.blue,
                        ),
                        _buildSensorCard(
                          'Soil Moisture',
                          '${sensorData['soil_moisture']?.toStringAsFixed(0) ?? '--'}%',
                          Icons.grass,
                          Colors.brown,
                        ),
                        _buildSensorCard(
                          'Moisture Status',
                          (sensorData['soil_moisture'] ?? 0) >= 40 &&
                                  (sensorData['soil_moisture'] ?? 0) <= 70
                              ? 'Safe'
                              : 'Unsafe',
                          Icons.security,
                          (sensorData['soil_moisture'] ?? 0) >= 40 &&
                                  (sensorData['soil_moisture'] ?? 0) <= 70
                              ? Colors.green
                              : Colors.red,
                        ),
                      ],
                    ),
                    
                    const SizedBox(height: 24),
                    
                    // Control Buttons
                    const Text(
                      'Controls',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    
                    const SizedBox(height: 16),
                    
                    ElevatedButton.icon(
                      onPressed: checkConditions,
                      icon: const Icon(Icons.check_circle),
                      label: const Text('Check Spray Conditions'),
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.all(16),
                      ),
                    ),
                    
                    const SizedBox(height: 12),
                    
                    Row(
                      children: [
                        Expanded(
                          child: ElevatedButton.icon(
                            onPressed: () => controlSpray('START'),
                            icon: const Icon(Icons.play_arrow),
                            label: const Text('Start Spray'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.green,
                              padding: const EdgeInsets.all(16),
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: ElevatedButton.icon(
                            onPressed: () => controlSpray('STOP'),
                            icon: const Icon(Icons.stop),
                            label: const Text('Stop Spray'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.red,
                              padding: const EdgeInsets.all(16),
                            ),
                          ),
                        ),
                      ],
                    ),
                    
                    const SizedBox(height: 24),
                    
                    // Scan Button
                    ElevatedButton.icon(
                      onPressed: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => const ScanScreen(),
                          ),
                        );
                      },
                      icon: const Icon(Icons.camera_alt, size: 32),
                      label: const Text(
                        'Scan Leaf for Disease',
                        style: TextStyle(fontSize: 18),
                      ),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.purple,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.all(20),
                      ),
                    ),
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildSensorCard(
      String title, String value, IconData icon, Color color) {
    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 40, color: color),
            const SizedBox(height: 8),
            Text(
              title,
              style: const TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w500,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 4),
            Text(
              value,
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class ScanScreen extends StatefulWidget {
  const ScanScreen({Key? key}) : super(key: key);

  @override
  State<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends State<ScanScreen> {
  final String apiUrl = 'http://192.168.1.100:5000';
  final ImagePicker _picker = ImagePicker();
  File? _image;
  bool isAnalyzing = false;
  Map<String, dynamic>? analysisResult;

  Future<void> pickImage(ImageSource source) async {
    final pickedFile = await _picker.pickImage(source: source);
    
    if (pickedFile != null) {
      setState(() {
        _image = File(pickedFile.path);
        analysisResult = null;
      });
    }
  }

  Future<void> analyzeImage() async {
    if (_image == null) return;
    
    setState(() => isAnalyzing = true);
    
    try {
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('$apiUrl/analyze'),
      );
      
      request.files.add(
        await http.MultipartFile.fromPath('image', _image!.path),
      );
      
      var response = await request.send();
      var responseData = await response.stream.bytesToString();
      var data = json.decode(responseData);
      
      setState(() {
        analysisResult = data;
        isAnalyzing = false;
      });
    } catch (e) {
      setState(() => isAnalyzing = false);
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('Error'),
          content: Text('Failed to analyze image: $e'),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('OK'),
            ),
          ],
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('🔬 Disease Analysis'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Image Selection
            if (_image == null)
              Container(
                height: 200,
                decoration: BoxDecoration(
                  color: Colors.grey[300],
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Center(
                  child: Text(
                    'No image selected',
                    style: TextStyle(color: Colors.grey),
                  ),
                ),
              )
            else
              ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: Image.file(
                  _image!,
                  height: 300,
                  fit: BoxFit.cover,
                ),
              ),
            
            const SizedBox(height: 16),
            
            // Image Selection Buttons
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () => pickImage(ImageSource.camera),
                    icon: const Icon(Icons.camera_alt),
                    label: const Text('Camera'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () => pickImage(ImageSource.gallery),
                    icon: const Icon(Icons.photo_library),
                    label: const Text('Gallery'),
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 16),
            
            // Analyze Button
            if (_image != null)
              ElevatedButton.icon(
                onPressed: isAnalyzing ? null : analyzeImage,
                icon: isAnalyzing
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.search),
                label: Text(isAnalyzing ? 'Analyzing...' : 'Analyze Leaf'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.purple,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.all(16),
                ),
              ),
            
            const SizedBox(height: 24),
            
            // Analysis Results
            if (analysisResult != null) ...[
              const Text(
                'Analysis Results',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 16),
              Card(
                color: (analysisResult!['disease_detected'] ?? false)
                    ? Colors.red[50]
                    : Colors.green[50],
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        analysisResult!['disease_name'] ?? 'Unknown',
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        analysisResult!['disease_description'] ?? '',
                        style: TextStyle(color: Colors.grey[700]),
                      ),
                      const Divider(height: 24),
                      _buildResultRow(
                        'Infection Level',
                        '${analysisResult!['infection_level']?.toStringAsFixed(1) ?? '--'}%',
                      ),
                      _buildResultRow(
                        'Severity',
                        analysisResult!['severity'] ?? '--',
                      ),
                      _buildResultRow(
                        'Confidence',
                        '${analysisResult!['confidence']?.toStringAsFixed(1) ?? '--'}%',
                      ),
                      const Divider(height: 24),
                      _buildResultRow(
                        'Recommended Pesticide',
                        analysisResult!['pesticide'] ?? '--',
                      ),
                      _buildResultRow(
                        'Dosage',
                        analysisResult!['dosage'] ?? '--',
                      ),
                      _buildResultRow(
                        'Spray Duration',
                        '${analysisResult!['spray_duration'] ?? '--'} seconds',
                      ),
                      const SizedBox(height: 16),
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: (analysisResult!['spray_recommended'] ?? false)
                              ? Colors.green[100]
                              : Colors.orange[100],
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Row(
                          children: [
                            Icon(
                              (analysisResult!['spray_recommended'] ?? false)
                                  ? Icons.check_circle
                                  : Icons.warning,
                              color: (analysisResult!['spray_recommended'] ??
                                      false)
                                  ? Colors.green
                                  : Colors.orange,
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                (analysisResult!['spray_recommended'] ?? false)
                                    ? '✅ Spraying recommended'
                                    : '⚠️ ${analysisResult!['alert_message']?.split('\n').last ?? 'Spraying not recommended'}',
                                style: TextStyle(
                                  color: (analysisResult!['spray_recommended'] ??
                                          false)
                                      ? Colors.green[800]
                                      : Colors.orange[800],
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildResultRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: const TextStyle(fontWeight: FontWeight.w500),
          ),
          Text(
            value,
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
        ],
      ),
    );
  }
}
