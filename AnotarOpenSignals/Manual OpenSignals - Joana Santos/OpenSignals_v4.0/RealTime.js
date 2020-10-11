$(function() {
	$("#record").click(function() {
		$("#Popup").hide()
		offline = false;
		if (!recordSaved) { //record not saved previously
			confirmPopup('top', "Do you want to <b>save</b><br> the previous record?", "record", -140, 40)
			
			$("#okPopup").unbind('click').click(function() {
				SendDir();
				
				$("#ConfirmCheck").unbind('click').click(function() {
					if ($("#fileName").attr('value') == "") {
						$("#popMessage").html("PLEASE INSERT FILE NAME");
						$("#popMessage").show();
					}else {
						
						var path = $('#pathName').attr('value');
						path = path.replace(/\\/g,"\\\\");
						var file = $('#fileName').attr('value');
						type=$("#fileFormat").find(":selected")[0].id
						ws.send("checkFile('"+path+"','"+file+"','"+type+"')");
					}
				})
				$("#Popup").hide()
			})
			$("#cancelPopup").unbind('click').click(function() {
				$("#Popup").hide()
				playOf = false;
				recordSaved = false;
				$("#recordingDigital").show();
				options = {
					xaxis: {show:false, color: 'grey',tickColor:"#C2C2C2"}, 
					yaxis: {show:true,color: 'grey',tickColor:"#C2C2C2",min:0,max:1024},
					series: {
						lines: { show: true, lineWidth: 1.2 },
						points: { show: false,fill:false,radius:0.5 },
						shadowSize: 0
					},
					grid: {backgroundColor: "transparent",borderColor:"#C2C2C2",borderWidth:1 }
				};
				optOverview = {
					series: {
						lines: { show: true, lineWidth: 1.2 ,tickColor:"#571F8B"},
						points: { show: false },
						shadowSize: 0,
					},
					selection: { mode: "x"},
					legend:false,
					xaxis: {show:false,color:"grey",tickColor:"#C2C2C2"},
					yaxis: {show:false,min:0,max:1026},
					grid: {backgroundColor: "transparent" ,borderColor:"#C2C2C2",borderWidth:0.5}
				}; 
				if (connection) {
					
					if (macAddress == '') {
						//alert('Select a device in the configurations menu.');
						popup('top', 'Select a device in the <b>configurations</b> menu', 'record', -160, 50)
						recordSaved = true;
					} else {
						record = true;
						config();
						acquisitionSet = true;
						play = true
						$("#Loading").fadeOut(100)
						$("#WelcomePage").fadeOut(100)
						$("#MainWelcome").fadeOut(100)
						setTimeout(function() {
							$("#load").fadeIn(100)
							$("#ELAPSED").show();
							document.getElementById("ELAPSED").innerHTML = "00:00:00"
							if (samplingRate == 1000) {nSamples = 300}
							else if (samplingRate == 100) {nSamples = 12}
							else if (samplingRate == 10) {nSamples = 1}
							else if (samplingRate == 1) {nSamples = 1}
							marks = [{lineWidth: 1,color:'lightGrey',xaxis:{from:0,to:0}}]
							xmin = 10;
							document.getElementById("timeScale").innerHTML = xmin+"s"
							AxisShow = false
							ws.send('SetupAcquisition("'+macAddress+'",'+JSON.stringify(ch)+','+samplingRate+','+JSON.stringify(units)+')')
							
							
						},500)
					}
				}
				
			})
		} else {
		
			playOf = false;
			recordSaved = false;
			$("#recordingDigital").show();
			options = {
				xaxis: {show:false, color: 'grey',tickColor:"#C2C2C2"}, 
				yaxis: {show:true,color: 'grey',tickColor:"#C2C2C2",min:0,max:1024},
				series: {
					lines: { show: true, lineWidth: 1.2 },
					points: { show: false,fill:false,radius:0.5 },
					shadowSize: 0
				},
				grid: {backgroundColor: "transparent",borderColor:"#C2C2C2",borderWidth:1 }
			};
			optOverview = {
				series: {
					lines: { show: true, lineWidth: 1.2 ,tickColor:"#571F8B"},
					points: { show: false },
					shadowSize: 0,
				},
				selection: { mode: "x"},
				legend:false,
				xaxis: {show:false,color:"grey",tickColor:"#C2C2C2"},
				yaxis: {show:false,min:0,max:1026},
				grid: {backgroundColor: "transparent" ,borderColor:"#C2C2C2",borderWidth:0.5}
			}; 
			if (connection) {
				
				if (macAddress == '') {
					//alert('Select a device in the configurations menu.');
					popup('top', 'Select a device in the <b>configurations</b> menu', 'record', -160, 50)
					recordSaved = true;
				} else {
					record = true;
					config();
					acquisitionSet = true;
					play = true
					$("#Loading").fadeOut(100)
					$("#WelcomePage").fadeOut(100)
					$("#MainWelcome").fadeOut(100)
					setTimeout(function() {
						$("#load").fadeIn(100)
						$("#ELAPSED").show();
						document.getElementById("ELAPSED").innerHTML = "00:00:00"
						if (samplingRate == 1000) {nSamples = 300}
						else if (samplingRate == 100) {nSamples = 12}
						else if (samplingRate == 10) {nSamples = 1}
						else if (samplingRate == 1) {nSamples = 1}
						marks = [{lineWidth: 1,color:'lightGrey',xaxis:{from:0,to:0}}]
						xmin = 10;
						document.getElementById("timeScale").innerHTML = xmin+"s"
						AxisShow = false
						ws.send('SetupAcquisition("'+macAddress+'",'+JSON.stringify(ch)+','+samplingRate+','+JSON.stringify(units)+')')
						
						
					},500)
				}
			}
		}
		
	})
	
	$("#record").mouseenter(function() {
		$("#colorCircleSmall").css({'display':'block'});
		$("#colorCircle").css({'display':'none'});
	})
	
	$("#saveConfig").mouseover(function() {
		$(this).attr({src:'Img/new/certo_azul.png'});
	})
	$("#saveConfig").mouseout(function() {
		$(this).attr({src:'Img/new/certo_cinza.png'});
	})
	$("#saveConfig").click(function() {
		config();
		
	})
	$("#cancelConfig").mouseover(function() {
		$(this).attr({src:'Img/new/errado_azul.png'});
	})
	$("#cancelConfig").mouseout(function() {
		$(this).attr({src:'Img/new/errado_cinza.png'});
	})
	$("#cancelConfig").click(function() {
		$("#configurations").fadeOut(300)
		optionsMenuOpen = false
	})
	$("#save").mouseover(function() {
		$(this).attr({src:'Img/new/save_1.png'});
	})
	$("#save").mouseout(function() {
		$(this).attr({src:'Img/new/save_cinza.png'});
	})
	$("#save").click(function() {
		offline = false;
		$("#Popup").hide()
		$("#goBack").hide()
		playOf = false;
		if (BeginApp == false) {
			SendDir();
			$("#ConfirmCheck").unbind('click').click(function() {
				if ($("#fileName").attr('value') == "") {
					$("#popMessage").html("PLEASE INSERT FILE NAME");
					$("#popMessage").show();
				}else {
					
					var path = $('#pathName').attr('value');
					path = path.replace(/\\/g,"\\\\");
					var file = $('#fileName').attr('value');
					type=$("#fileFormat").find(":selected")[0].id
					ws.send("checkFile('"+path+"','"+file+"','"+type+"')");
				}
			})
		}
		else { 
			// alert("You can only save after doing a record!")
			popup('top', "You can only save after doing a <b>record</b>", 'save', -160, 30)
		}
	})
	
	$("#annotationKeys").keydown(function (e) {
		
		if ($.inArray(e.keyCode, annotationKeys) == -1) {
			if (e.keyCode <= 90 & e.keyCode >= 48){
				setAnnotationCells(e.keyCode,"");
				/*$("#annotationKeyCells").show()
				annotationKeys.push(e.keyCode)
				character = String.fromCharCode(e.keyCode)
				$("#annotationKeyCells").append('<tr id="tr-'+e.keyCode+'"><td>'+character+'</td><td><input id="input-'+e.keyCode+'" type="text" /></td><td><img id="'+e.keyCode+'" src="Img/new/errado_cinza.png" height="22px" /></td></tr>')
				*/
				$("#"+e.keyCode).unbind('click').click(function() {
					$("#tr-"+e.keyCode).remove();
					annotationKeys.splice(annotationKeys.indexOf(e.keyCode),1);
					if (annotationKeys.length == 0) {$("#annotationKeyCells").hide();}
				})
			}
		}
		
	})
	
	$("#annotationKeys").keyup(function (e) {
		$("#annotationKeys").val("");
	})
	
	
	
})

function setAnnotationCells(key,description) {
	$("#annotationKeyCells").show()
	annotationKeys.push(key)
	character = String.fromCharCode(key)
	if (description == "") {
		$("#annotationKeyCells").append('<tr id="tr-'+key+'"><td>'+character+'</td><td><input id="input-'+key+'" type="text" /></td><td><img id="'+key+'" src="Img/new/errado_cinza.png" height="22px" /></td></tr>');
	} else {
		$("#annotationKeyCells").append('<tr id="tr-'+key+'"><td>'+character+'</td><td><input id="input-'+key+'" type="text" value="'+description+'" /></td><td><img id="'+key+'" src="Img/new/errado_cinza.png" height="22px" /></td></tr>');
	}
	$("#"+key).unbind('click').click(function() {
		$("#tr-"+key).remove();
		annotationKeys.splice(annotationKeys.indexOf(key),1);
		if (annotationKeys.length == 0) {
			for (an=1;a<$("#annotationKeyCells tr");a++) {
				$("#annotationKeyCells tr")[a].remove();
			}
			$("#annotationKeyCells").hide();
		}
	})
	}



function config() {
	// record = true;
	connection=false;
	macAddress = $("#MacAdd").attr('value')
	device = $("#Device").attr('value')
	mylist = document.getElementById('samplingRate')
	samplingRate = mylist.options[mylist.selectedIndex].text;
	
	var checkbox = $("#contentConfig").parent().find("input[type=checkbox]:checked");
	ch=[]
	labels = []
	units = []
	for (x=0;x<6;x++) {
		labels.push($("#A"+x+"t").attr('value'))
		units.push($("#unit"+x).val())
	}
	for (x=0;x<checkbox.length;x++) {
		ch.push(parseInt(checkbox[x].id.slice(-1)))
	}
	ws.send('saveConfig("'+device+'","'+macAddress+'",'+JSON.stringify(ch)+','+JSON.stringify(digitalOut)+','+JSON.stringify(labels)+','+JSON.stringify(units)+','+JSON.stringify(annotationKeysJSON)+')')
}

function Connect(state) {
	
	if (state == true) { //Successful connection to device
		ws.send('StartAcquisition()')
		AxisShow = true
		AcqShoworHide = true;
		
	} else { //No connected to device
		$("#WelcomePage").fadeIn(100);
		$("#MainWelcome").fadeIn(100);$("#Loading").fadeIn(100); 
		$("#load").fadeOut(100)
		play = true
		acquisitionSet = false;
		
		if (macAddress == '') { 
			//alert('Select a device in the configurations menu.');
			popup('top', 'Select a device in the <b>configurations</b> menu', 'record', -160, 50)
			recordSaved = true;
		} else {
			// alert("Connection failed! \nCheck if your device or Bluetooth receiver are connected.")
			setTimeout(function() {popup('top', "<b>Connection failed!</b> <br><font size='2'>Check your device or Bluetooth receiver connectivity.</font>", 'record', -160, 50)},1000);
			
			recordSaved = true;
			record = false;
		}
		
	}
}

function configurations() {
	$("#Popup").hide()
	optionsMenuOpen = true
	
	$("#configurations").fadeIn(300)
}

function SetConfigurations(sets,dev) {
	
	Settings = sets;
	Devices = dev;
	macAddress = Settings.MacAddress;
	annotationKeysJSON = Settings.AnotKeys;
	$("#MacAdd").attr('value',macAddress)
	$("#Device").attr('value',Settings.Device)
	$("#devices").empty()

	for (x=0;x<6;x++) {$("#A"+x+"t").attr('value',Settings.Labels[x]);$("#unit"+x).val(Settings.Units[x]);}
	$("#contentConfig").parent().find('input[type=checkbox]:checked').removeAttr('checked');
		
	for (an in Settings.Analog) {
		$('#A'+Settings.Analog[an]).attr('checked','checked');
		changeCheckboxStyle("A"+Settings.Analog[an])
	}
	var checkbox = $("#contentConfig").parent().find("input[type=checkbox]:checked");
	dt = {};
	ch=[];
	
	for (x=0;x<checkbox.length;x++) {
		id = checkbox[x].id +"t";
		name = Settings.Labels[parseInt(checkbox[x].id.slice(-1))];
		if (Settings.Units[parseInt(checkbox[x].id.slice(-1))] == "None") {
			dt[x] = {"id":parseInt(checkbox[x].id.slice(-1)),"label": name,"data":[],"anot":[]};
		} else {
			dt[x] = {"id":parseInt(checkbox[x].id.slice(-1)),"label": name+" ["+Settings.Units[parseInt(checkbox[x].id.slice(-1))]+"]","data":[],"anot":[]};
		}
		ch.push(parseInt(checkbox[x].id.slice(-1)));
	}
	
	if (record) {
		units = Settings.Units;
		ws.send('getRTDatatoFlot('+JSON.stringify(dt)+')');
	} else {
		connection = true;
		$("#MenuLogo").fadeIn(100);
		$("#boxToFlip").fadeIn(100);
	}
	
	$("#configurations").fadeOut(300)
	optionsMenuOpen = false
	digitalOut = Settings.Digital
	for (d in digitalOut) {
		if (digitalOut[3-d] == 0) {
			$("#DO"+d).attr("src","Img/new/botao.png")
		} else {
			$("#DO"+d).attr("src","Img/new/botao_azul.png")
		}
	}
	annotationKeys = []
	for (k in annotationKeysJSON) {
		setAnnotationCells(k,annotationKeysJSON[k]);
	}
	
}

function DeviceSelect() {
	option = $("#Device").attr('value')
	console.log('Device Select')
	macAddress = Devices[option]
}

function changeYScale(UpOrDown) {
	trSelected=$(".graphSelected")
	
	if (trSelected.length > 0) { //there is a plot selected
		if (UpOrDown == 'up') {
			for (tr=0;tr<trSelected.length;tr++) {
				if (MaxOffset[trSelected[tr].id.slice(-1)] < 1034) {
					MaxOffset[trSelected[tr].id.slice(-1)]+=(limits[units[data[trSelected[tr].id.slice(-1)].id]][1]-limits[units[data[trSelected[tr].id.slice(-1)].id]][0])*0.05
					MinOffset[trSelected[tr].id.slice(-1)]+=(limits[units[data[trSelected[tr].id.slice(-1)].id]][1]-limits[units[data[trSelected[tr].id.slice(-1)].id]][0])*0.05
				}
			}
		} else if (UpOrDown == 'down') {
			for (tr=0;tr<trSelected.length;tr++) {
				if (MinOffset[trSelected[tr].id.slice(-1)] > -10) {
					MaxOffset[trSelected[tr].id.slice(-1)]-=(limits[units[data[trSelected[tr].id.slice(-1)].id]][1]-limits[units[data[trSelected[tr].id.slice(-1)].id]][0])*0.05
					MinOffset[trSelected[tr].id.slice(-1)]-=(limits[units[data[trSelected[tr].id.slice(-1)].id]][1]-limits[units[data[trSelected[tr].id.slice(-1)].id]][0])*0.05
				}
			}
		}
	} else { // apply changing to all plots
		if (UpOrDown == 'up') {
			for (var i in dataGeral) {
				if (i.indexOf('Analog') != -1) {
					if (MaxOffset[i.slice(-1)] < 1034) {
						MaxOffset[i.slice(-1)]+=(limits[units[data[i.slice(-1)].id]][1]-limits[units[data[i.slice(-1)].id]][0])*0.05;
						MinOffset[i.slice(-1)]+=(limits[units[data[i.slice(-1)].id]][1]-limits[units[data[i.slice(-1)].id]][0])*0.05;
					}
				}
			}
			
		} else if (UpOrDown == 'down') {
			for (var i in dataGeral) {
				if (i.indexOf('Analog') != -1) {
					if (MinOffset[i.slice(-1)] > -10) {
						MaxOffset[i.slice(-1)]-=(limits[units[data[i.slice(-1)].id]][1]-limits[units[data[i.slice(-1)].id]][0])*0.05;
						MinOffset[i.slice(-1)]-=(limits[units[data[i.slice(-1)].id]][1]-limits[units[data[i.slice(-1)].id]][0])*0.05;
					}
				}
			}
		}
	}
}

function Zooming(InOrOut) {
	trSelected=$(".graphSelected")
	if (trSelected.length > 0) { //there is a plot selected
		if (InOrOut == 'in') { // (+)
			for (tr=0;tr<trSelected.length;tr++) {
				MaxOffset[trSelected[tr].id.slice(-1)]-=(limits[units[data[trSelected[tr].id.slice(-1)].id]][1]-limits[units[data[trSelected[tr].id.slice(-1)].id]][0])*0.05
				MinOffset[trSelected[tr].id.slice(-1)]+=(limits[units[data[trSelected[tr].id.slice(-1)].id]][1]-limits[units[data[trSelected[tr].id.slice(-1)].id]][0])*0.05
				if (MaxOffset[trSelected[tr].id.slice(-1)]-MinOffset[trSelected[tr].id.slice(-1)] < (limits[units[data[trSelected[tr].id.slice(-1)].id]][1]-limits[units[data[trSelected[tr].id.slice(-1)].id]][0])*0.05) {
					MaxOffset[trSelected[tr].id.slice(-1)]+=(limits[units[data[trSelected[tr].id.slice(-1)].id]][1]-limits[units[data[trSelected[tr].id.slice(-1)].id]][0])*0.05
					MinOffset[trSelected[tr].id.slice(-1)]-=(limits[units[data[trSelected[tr].id.slice(-1)].id]][1]-limits[units[data[trSelected[tr].id.slice(-1)].id]][0])*0.05
				}
			}
		} else if (InOrOut == 'out') { // (-)
			for (tr=0;tr<trSelected.length;tr++) {
				MaxOffset[trSelected[tr].id.slice(-1)]+=(limits[units[data[trSelected[tr].id.slice(-1)].id]][1]-limits[units[data[trSelected[tr].id.slice(-1)].id]][0])*0.05
				MinOffset[trSelected[tr].id.slice(-1)]-=(limits[units[data[trSelected[tr].id.slice(-1)].id]][1]-limits[units[data[trSelected[tr].id.slice(-1)].id]][0])*0.05
			}
		}
	} else { // apply zooming to all plots
		if (InOrOut == 'in') { // (+)
			for (var i in dataGeral) {
				if (i.indexOf('Analog') != -1) {
					MaxOffset[i.slice(-1)]-=(limits[units[data[i.slice(-1)].id]][1]-limits[units[data[i.slice(-1)].id]][0])*0.05;
					MinOffset[i.slice(-1)]+=(limits[units[data[i.slice(-1)].id]][1]-limits[units[data[i.slice(-1)].id]][0])*0.05;
					if (MaxOffset[i.slice(-1)]-MinOffset[i.slice(-1)] < (limits[units[data[i.slice(-1)].id]][1]-limits[units[data[i.slice(-1)].id]][0])*0.05) {
						MaxOffset[i.slice(-1)]+=(limits[units[data[i.slice(-1)].id]][1]-limits[units[data[i.slice(-1)].id]][0])*0.05;
						MinOffset[i.slice(-1)]-=(limits[units[data[i.slice(-1)].id]][1]-limits[units[data[i.slice(-1)].id]][0])*0.05;
					}
				}
			}
			
		} else if (InOrOut == 'out') { // (-)
			for (var i in dataGeral) {
				if (i.indexOf('Analog') != -1) {
				MaxOffset[i.slice(-1)]+=(limits[units[data[i.slice(-1)].id]][1]-limits[units[data[i.slice(-1)].id]][0])*0.05;
				MinOffset[i.slice(-1)]-=(limits[units[data[i.slice(-1)].id]][1]-limits[units[data[i.slice(-1)].id]][0])*0.05;
				}
			}
		}
	}
}

function NewXScale(scale) {
	//xmin = 60-scale
	/*overviewPlot.setSelection({xaxis:{from:xmin,to:xmax}},true);*/
	xmin = scale
	document.getElementById("timeScale").innerHTML = scale+"s"
}

function digitalOutputs (n) {
	if ($("#DO"+n).attr('src') =='Img/new/botao_azul.png') {
		digitalOut[3-n] = 0
		$("#DO"+n).attr('src','Img/new/botao.png')
	} else {
		digitalOut[3-n] = 1
		$("#DO"+n).attr('src','Img/new/botao_azul.png')
	}
	ws.send("digitalOutputs("+JSON.stringify(digitalOut)+")")
}

function DevicesPage() {
	$('#Popup').hide();
	$("#configurations").hide()
	$("#BackDevices").hide();
	$("#configurationsDevices").show()
	
	$("#oldDevices").empty()
	for (var d in Devices) {
		$("#oldDevices").append('<tr><td><h4 id="'+Devices[d][0]+'" style="font-family:arial;margin:5px;text-align:left">'+Devices[d][1]+'</h4><p style="font-size:12px;font-family:arial;margin:5px;text-align:left">'+Devices[d][0]+'</p></td></tr>')
	}
	ws.send('search()')
	$("#SearchNewDevices").text('Searching...')
	$('#loadDevices').show();
	$("#oldDevices h4").click(function(e) {
		$("#newDevices").empty()
		$("#oldDevices").empty()
		macAddress = e.srcElement.id
		$("#MacAdd").attr('value',macAddress)
		$("#Device").attr('value',e.srcElement.innerText)
		$("#configurationsDevices").hide()
		$("#configurations").show()
		
	})
	
}

function SearchDevices(Dev) {
	$("#newDevices").empty()
	$("#loadDevices").hide()
	if (Dev == -1) {
		//alert('The Bluetooth adapter is not connected')
		setTimeout(function() {popup('top', 'The Bluetooth adapter is <b>not connected</b>', 'SearchNewDevices', -150, 150)},1000)
		
	}
	else if (Dev['new'].length == 0) {
		$("#newDevices").append('<p style="font-size:12px;font-family:arial;margin:5px;text-align:left">No new devices found.</p>')
	} else {
		for (var d in Dev['new']) {
			name = Dev['new'][d][1]
			if (name == '') {name='Unknow'}
			$("#newDevices").append('<tr><td><h4 id="'+Dev['new'][d][0]+'" style="font-family:arial;margin:5px;text-align:left">'+name+'</h4><p style="font-size:12px;font-family:arial;margin:5px;text-align:left">'+Dev['new'][d][0]+'</p></td></tr>')
		}
	}
	$("#SearchNewDevices").text('Search new devices')
	$("#newDevices h4").click(function(e) {
		$("#newDevices").empty()
		$("#oldDevices").empty()
		macAddress = e.srcElement.id
		$("#MacAdd").attr('value',macAddress)
		$("#Device").attr('value',e.srcElement.innerText)
		$("#configurationsDevices").hide()
		$("#configurations").show()
		$('#Popup').hide();
	})
	$("#BackDevices").show();
	
}

var seconds = null;
var ticker = null;

function tick(seconds)
{
	var secs = seconds;
	var hrs = Math.floor( secs / 3600 );
	secs %= 3600;
	var mns = Math.floor( secs / 60 );
	secs %= 60;
	var Time = ( hrs < 10 ? "0" : "" ) + hrs
				 + ":" + ( mns < 10 ? "0" : "" ) + mns
				 + ":" + ( secs < 10 ? "0" : "" ) + Math.floor(secs);
	//var Time = ( mns < 10 ? "0" : "" ) + mns
				//+ ":" + ( secs < 10 ? "0" : "" ) + Math.floor(secs);
    document.getElementById("ELAPSED").innerHTML = Time;
}

function SetAnnotationKeys() {
	$("#configurations").hide();
	$("#SetAnnotationPage").show();
}

function SaveAnnotationKeys() {
	annotationKeysJSON = {}
	$.each(annotationKeys, function( index, value ) {
		description = $("#input-"+value).val();
		if (description == "") {
			annotationKeysJSON[value] = String.fromCharCode(value);
		} else {
			annotationKeysJSON[value] = description;
		}
	});
}

