import json
import rclpy
from nav_msgs.msg import Odometry
import rclpy
from rclpy.node import Node
import sys
import os

import random
import time

from paho.mqtt import client as mqtt_client

class ElasticMqtt:
    def __init__(self, broker, port, topic):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.client_id = f'python-mqtt-{random.randint(0, 1000)}'
        self.client = self.connect_mqtt()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    def connect_mqtt(self):
        client = mqtt_client.Client(self.client_id)
        client.on_connect = self.on_connect
        client.connect(self.broker, self.port)
        return client

    def publish(self, msg):
        result = self.client.publish(self.topic, msg)
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{self.topic}`")
        else:
            print(f"Failed to send message to topic {self.topic}")

    def run(self):
        self.client.loop_start()

class ElasticSub(Node):

    def pub_mqtt(self, msg_json):
        self._elastic_mqtt.publish(msg_json)


    def __init__(self):
        super().__init__('ElasticSub')
        self.subscription = self.create_subscription(
            Odometry,
            '/odom',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning
        
        broker = 'ec2-3-82-196-231.compute-1.amazonaws.com'
        port = 1883
        topic = "robot/robot01"

        self._elastic_mqtt = ElasticMqtt(broker, port, topic)
        self._elastic_mqtt.run()
  
    def listener_callback(self, msg):
        self.get_logger().info("Odom:")
        # Extract relevant values from message
        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y
        z = msg.pose.pose.position.z
        qx = msg.pose.pose.orientation.x
        qy = msg.pose.pose.orientation.y
        qz = msg.pose.pose.orientation.z
        qw = msg.pose.pose.orientation.w

        # Print extracted values
        self.get_logger().info(f"Position: ({x:.2f}, {y:.2f}, {z:.2f})")
        self.get_logger().info(f"Orientation: ({qx:.2f}, {qy:.2f}, {qz:.2f}, {qw:.2f})")

         # Create a dictionary with the extracted values
        data = {"odom": {
            "position": {"x": round(x, 2), "y": round(y, 2), "z": round(z, 2)},
            "orientation": {"x": round(qx, 2), "y": round(qy, 2), "z": round(qz, 2), "w": round(qw, 2)},
        }}

        # Convert the dictionary to a JSON object
        json_data = json.dumps(data)
        
        # Publish the JSON data to the MQTT topic
        self.pub_mqtt(json_data)


def main(args=None):
    rclpy.init(args=args)

    elastic_subscriber = ElasticSub()

    rclpy.spin(elastic_subscriber)

    elastic_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

