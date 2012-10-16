package br.com.badriciobq;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;

import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Binder;
import android.os.Bundle;
import android.os.Environment;
import android.os.IBinder;
import android.util.Log;

public class GetLocation extends Service implements Localizacao{

	private FileOutputStream arquivo;
	private LocationManager locationManager;
	private LocationListener listener;
	
	double latitude, longitude, altitude;
	float speed, precisao;
	long timestamp;
	
	private final IBinder conexao = new LocalBinder();
	
	public class LocalBinder extends Binder{
		public Localizacao getLocalizacao(){
			return GetLocation.this;
		}
	}
	
	public IBinder onBind(Intent intent) {
		return conexao;
	}
	
	public void onCreate() {
		super.onCreate();
		
		File file;
		
		try {
			
			SimpleDateFormat sdf = new SimpleDateFormat("yyyyMMdd-HHmmss");
			String ARQUIVO = sdf.format(new Date()) + ".trace";
			
			File path = new File(Environment.getExternalStorageDirectory() + "/VeNeM");
			
			if(path.isDirectory())
				file = new File(path, ARQUIVO);
			else if(path.mkdirs())
				file = new File(path, ARQUIVO);
			else
				file = new File(Environment.getExternalStorageDirectory(), ARQUIVO);
				
						
			arquivo = new FileOutputStream(file, true);
			listener = new LocationListener() {
				
				public void onStatusChanged(String arg0, int arg1, Bundle arg2) {	}
				
				public void onProviderEnabled(String arg0) {   }
				
				public void onProviderDisabled(String arg0) {	}
				
				public void onLocationChanged(Location loc) {
					
					if(loc.getLatitude() != latitude && loc.getLongitude() != longitude){
						latitude = loc.getLatitude();
						longitude = loc.getLongitude();
						altitude = loc.getAltitude();
						timestamp = loc.getTime();
						speed = loc.getSpeed();
						precisao = loc.getAccuracy();

						String lin = latitude + "," + longitude + "," + altitude + "," + timestamp + "," + speed + "\n";

						try {

							arquivo.write(lin.getBytes());
							arquivo.flush();

						} catch (IOException e) {
							Log.v("GETLOCATION", "Não foi possível escrever no arquivo");
						}
					}
				}
			};
			
			locationManager = (LocationManager) getSystemService(Context.LOCATION_SERVICE);
			locationManager.requestLocationUpdates(LocationManager.GPS_PROVIDER, 0, 0, listener);

			
		} catch (FileNotFoundException e) {
			Log.v("GETLOCATION", "Arquivo não encontrado");
		}	
	}
	
	public void onDestroy() {
		super.onDestroy();
		
		locationManager.removeUpdates(listener);
		
		try {
			arquivo.close();
			
		} catch (IOException e) {
			Log.v("GETLOCATION", "Erro ao fechar o arquivo");
		}
	}

	public double getLatitude() {
		return latitude;
	}

	public double getLongitude() {
		return longitude;
	}

	public double getAltitude() {
		return altitude;
	}

	public long getTime() {
		return timestamp;
	}

	public float getSpeed() {
		return speed;
	}
	
	public float getPrecisao(){
		return precisao;
	}
}
