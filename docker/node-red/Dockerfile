FROM nodered/node-red:latest

# Instalar nodos adicionales
RUN npm install --no-update-notifier --no-fund --no-audit --save \
    node-red-contrib-modbus \
    node-red-contrib-postgresql \
    node-red-node-serialport \
    node-red-node-pi-gpio
