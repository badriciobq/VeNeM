package br.com.badriciobq;

import br.com.badriciobq.GetLocation.LocalBinder;
import android.app.Activity;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.ServiceConnection;
import android.os.Bundle;
import android.os.Handler;
import android.os.IBinder;
import android.os.Message;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

public class MainActivity extends Activity implements ServiceConnection{
    
	private Button iniciar, parar;
	private ServiceConnection conexao;
	private TextView latitude, longitude, altitude, hora, velocidade, status, precisao;
	private Localizacao localizacao;
	private Handler handler;
	
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);
        
        conexao = this;
        iniciar = (Button) findViewById(R.id.start);
        parar = (Button) findViewById(R.id.stop);
        
        latitude = (TextView) findViewById(R.id.latitude);
        longitude = (TextView) findViewById(R.id.longitude);
        altitude = (TextView) findViewById(R.id.altitude);
        hora = (TextView) findViewById(R.id.hora);
        velocidade  = (TextView) findViewById(R.id.velocidade);
        status = (TextView) findViewById(R.id.status);
        precisao = (TextView) findViewById(R.id.precisao);
    }
    
    protected void onStart() {
    	super.onStart();
    	
    	final Intent servico = new Intent("SAVE_LOCATION");
    	
    	iniciar.setOnClickListener(new Button.OnClickListener() {
			public void onClick(View arg0) {
				
				if(bindService(new Intent(MainActivity.this, GetLocation.class), conexao, Context.BIND_AUTO_CREATE))
					Log.v("GETLOCATION", "Serviço iniciado");
				else
					Log.v("GETLOCATION", "Erro ao iniciar o serviço");
			}
		});
    	
    	parar.setOnClickListener( new Button.OnClickListener() {
			public void onClick(View v) {
				
				if(localizacao != null){
					unbindService(conexao);
					
					status.setText("Serviço parado");
					Log.v("GETLOCATION", "Serviço parado");
				}else
					Log.v("GETLOCATION", "Serviço já está parado");
				
			}
		});
    	

    	handler = new Handler(){
    		public void handleMessage(Message msg) {
    		    			
    			latitude.setText(msg.getData().getString("latitude"));
    			longitude.setText(msg.getData().getString("longitude"));
    			altitude.setText(msg.getData().getString("altitude"));
    			velocidade.setText(msg.getData().getString("velocidade"));
    			hora.setText(msg.getData().getString("hora"));
    			precisao.setText(msg.getData().getString("precisao"));
    		}
    	};

    	
    	new Thread( new Runnable() {
			public void run() {
				while(true){
					
					if (localizacao != null){
						
						Bundle pacote = new Bundle();
						pacote.putString("latitude", localizacao.getLatitude() + " ");
						pacote.putString("longitude", localizacao.getLongitude() + " ");
						pacote.putString("altitude", localizacao.getAltitude() + " ");
						pacote.putString("velocidade", localizacao.getSpeed() + " ");
						pacote.putString("hora", localizacao.getTime() + " ");
						pacote.putString("precisao", localizacao.getPrecisao() + " ");
						
						Message msg = new Message();
						msg.setData(pacote);
						handler.sendMessage(msg);	
					}
				}
			}
		}).start();
   }

	public void onServiceConnected(ComponentName arg0, IBinder arg1) {
		status.setText("Serviço está executando");
		LocalBinder binder = (LocalBinder) arg1;
		localizacao = binder.getLocalizacao();
	}

	public void onServiceDisconnected(ComponentName arg0) {		
		localizacao = null;
	}
    
}