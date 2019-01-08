# bankscraper


## Usage
configure in file docker-base.env
<pre><code>
    environment:
    - URL_BROKER=${URL_BROKER}
    - HOST_BROKER=${HOST_BROKER}
    - BROKER_CPF_CNPJ=${BROKER_CPF_CNPJ}
    - BROKER_PASSWORD=${BROKER_PASSWORD}
    - BROKER_DT_NASC=${BROKER_DT_NASC}
    - BROKER_SIGNATURE=${BROKER_SIGNATURE}
</code></pre>



### docker
<pre><code>
docker-compose up
</code></pre>

### rest
<pre><code>
Get localhost:5018/broker/change-stop
=> headers
    active:WDOQ18
    quantity:1
    operation:Buy
    stop_loss:25
    production:1
    change_position:1
    calculate_stop:0
    point_to_double:50
</code></pre>
