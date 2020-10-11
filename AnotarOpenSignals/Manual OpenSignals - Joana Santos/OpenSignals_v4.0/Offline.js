$(function() {
	$("#playOf").click(function() {
		$("#Popup").hide()
		if (BeginApp == true) {
			// alert("You can only visualize the signals after doing a record!")
			popup('top', "You can only visualize the signals after doing a <b>record</b>!", 'playOf', -125, 125)
		}else {
			FinalFile = "";
			offline = true;
			$("#recordingDigital").hide();
			record = false;
			options = {
				xaxis: {show:true, mode:"time",timeformat:"%M:%S.%f", minTickSize: [50, "millisecond"],color: 'grey',tickColor:"#C2C2C2"}, 
				yaxis: {show:true,color: 'grey',tickColor:"#C2C2C2",min:0,max:1024,panRange:[0,1023]},
				series: {
					lines: { show: true, lineWidth: 1.2 },
					points: { show: false,fill:false,radius:0.5 },
					shadowSize: 0
				},
				pan: {interactive: true	},
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
				xaxis: {show:true, mode:"time",timeformat:"%H:%M:%S",color:"grey",tickColor:"#C2C2C2"},
				yaxis: {show:false,min:0,max:1026},
				grid: {backgroundColor: "transparent" ,borderColor:"#C2C2C2",borderWidth:0.5}
			}; 
			$("#ELAPSED").hide();
			play = false;
			xMin = [];
			xMax = [];
			MinOffset = [];
			MaxOffset = [];
			ws.send("getDatatoFlot()");
			// $("#Loading").fadeOut(100);
			$("#WelcomePage").fadeOut(100);
			$("#MainWelcome").fadeOut(100);
			units=[];
			for (x=0;x<6;x++) {
				units.push("None");
			}
			playOf = true;
			
			
		}
	})
	
	$("#playOf").hover(function() {
		record = false;
		$("#colorCircle").css({'display':'block'});
		$("#colorCircleSmall").css({'display':'none'});
		console.log('enter mouse')
	})
	
	$("#openFile").mouseover(function() {
		$(this).attr({src:'Img/new/open_1.png'});
	})
	$("#openFile").mouseout(function() {
		$(this).attr({src:'Img/new/open_cinza.png'});
	})
	$("#openFile").click(function() {
		offline = true;
		$("#Popup").hide()
		SendDir();
		record = false;
		$("#recordingDigital").hide();
		options = {
			xaxis: {show:true, /*mode:"time",timeformat:"%M:%S.%f",*/ minTickSize: [50, "millisecond"],color: 'grey',tickColor:"#C2C2C2"}, 
			yaxis: {show:true,color: 'grey',tickColor:"#C2C2C2"},
			series: {
				lines: { show: true, lineWidth: 1.2 },
				points: { show: false,fill:false,radius:0.5 },
				shadowSize: 0
			},
			pan: {interactive: true	},
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
			xaxis: {show:true, mode:"time",timeformat:"%H:%M:%S",color:"grey",tickColor:"#C2C2C2"},
			yaxis: {show:false},
			grid: {backgroundColor: "transparent" ,borderColor:"#C2C2C2",borderWidth:0.5}
		}; 
	})
	
	$("#filename").click(function() {
		if ($("#CommentBox").is(':visible')) {
			$("#CommentBox").fadeOut(100);
			saveComment();
		} else {
			$("#CommentBox").fadeIn(100);
		}
	})
})

function saveComment() {
	comment = $("#comments").val()
	ws.send('saveComment("'+FinalFile+'","'+comment+'")')
}

function getComment(comment) {
	$("#comments").val(comment)
}

function plot(key,hov,click) {
	var d = [{data:data[key].data,color:data[key].color}];
	m=[];
	if (data[key].anot.length > 0) {
		var checkbox = $("#boxContentTable"+data[key].id+"_"+key).parent().find("input:checkbox");
		for (var x=0;x<checkbox.length;x++) {
			var xx = checkbox[x].id.split("_")[1]
			//if (data[key].anot[x].data.length != 0) {
				if ((annotating != key) || (annotating == key && xx != incAn)) {
					
					//var xx = checkbox[x].id.slice(5+(key.toString().length))
					
					if ($(checkbox[x]).is(":checked") /*& x!= incAn*/) {// check if checkbox is activated or not
						
						$("label[for='check"+key+"_"+xx+"']").css({background:data[key].anot[xx].color,"border-color":data[key].anot[xx].color});
						$("#name"+key+"_"+xx).css({color:"black"});
						for (var points in data[key].anot[xx].data) {
							if (data[key].anot[xx].data[points].length != 2) {
								m.push({ color: data[key].anot[xx].color, lineWidth: 1, xaxis: { from: (data[key].anot[xx].data[points]), to: (data[key].anot[xx].data[points]) } });
							} else {
								m.push({ color: data[key].anot[xx].color, lineWidth: 1, xaxis: { from: (data[key].anot[xx].data[points][0]), to: (data[key].anot[xx].data[points][1]) } });
							}
						}
					}else { //Change checkbox style when not checked
						$("label[for='check"+key+"_"+xx+"']").css({background:"transparent","border-color":"grey"});
						$("#name"+key+"_"+xx).css({color:"#A2A2A2"});
						
					}
				}
			//}
		}
		if (annotating == key) {
			for (var i in a) {
				if (a[i].length == undefined) {
					m.push(({ color: ListColorsAn[incAn], lineWidth: 1, xaxis: { from: a[i], to: a[i]} }));}
				else {
					m.push(({color:ListColorsAn[incAn],lineWidth: 1, xaxis: { from: a[i][0], to: a[i][1]} }));
				}
			}
			plots[key] = $.plot($("#placeholderAnalog"+key),d,$.extend(true, {}, options, {xaxis:{max:xMax[data[key].id],min:xMin[data[key].id],panRange:[data[key].data[0][0],data[key].data[data[key].data.length-1][0]]},yaxis:{min:MinOffset[data[key].id],max:MaxOffset[data[key].id],panRange:[MinOffset[data[key].id],MaxOffset[data[key].id]]},selection: { mode: "x",mouseClick:"right",color:ListColorsAn[incAn]},crosshair:{mode:'x',color:"black",lineWidth:0.5},grid: { markings:m,clickable:true,hoverable:true }}));
		} else {
			plots[key] = $.plot($("#placeholderAnalog"+key),d,$.extend(true, {}, options, {xaxis:{max:xMax[data[key].id],min:xMin[data[key].id],panRange:[data[key].data[0][0],data[key].data[data[key].data.length-1][0]]},yaxis:{min:MinOffset[data[key].id],max:MaxOffset[data[key].id],panRange:[MinOffset[data[key].id],MaxOffset[data[key].id]]},grid: { markings:m,clickable:click,hoverable:hov }}));
		}
	} else {
		if (annotating == key) {
			for (var i in a) {
				if (a[i].length == undefined) {
					m.push(({ color: ListColorsAn[incAn], lineWidth: 1, xaxis: { from: a[i], to: a[i]} }));}
				else {
					m.push(({color:ListColorsAn[incAn],lineWidth: 1, xaxis: { from: a[i][0], to: a[i][1]} }));
				}
			}
			plots[key] = $.plot($("#placeholderAnalog"+key),d,$.extend(true, {}, options, {xaxis:{max:xMax[data[key].id],min:xMin[data[key].id],panRange:[data[key].data[0][0],data[key].data[data[key].data.length-1][0]]},yaxis:{min:MinOffset[data[key].id],max:MaxOffset[data[key].id],panRange:[MinOffset[data[key].id],MaxOffset[data[key].id]]},selection: { mode: "x",mouseClick:"right",color:ListColorsAn[incAn]},crosshair:{mode:'x',color:"black",lineWidth:0.5},grid: { markings:m,clickable:true,hoverable:true }}));
		} else {
			plots[key] = $.plot($("#placeholderAnalog"+key),d,$.extend(true, {}, options, {xaxis:{max:xMax[data[key].id],min:xMin[data[key].id],panRange:[data[key].data[0][0],data[key].data[data[key].data.length-1][0]]},yaxis:{min:MinOffset[data[key].id],max:MaxOffset[data[key].id],panRange:[MinOffset[data[key].id],MaxOffset[data[key].id]]},grid: { clickable:click,hoverable:hov }}));
		}
	}
	plots[key].getPlaceholder().css('cursor','default')
	

}

function changeSelection(datasets) {
	trSelected=$(".graphSelected")
	console.log(datasets);
	for (var key in data) {
		if ((data[key].data[data[key].data.length-1][0] - data[key].data[0][0]) <= 70000) {
			options.xaxis.tickSize = 40;
		} else {
			options.xaxis.tickSize = 10000;
		}
		if (trSelected.length > 0){
			if ($("#tr"+data[key].id+"_"+key).attr('class') == 'graphic graphSelected') {
				xMin[data[key].id] = datasets[data[key].id].min;
				xMax[data[key].id] = datasets[data[key].id].max;
				overviewPlot[key].setSelection({xaxis:{from:xMin[data[key].id],to:xMax[data[key].id]}},true);
				CurrentDataset[data[key].id].data = datasets[data[key].id].data;
				CurrentDataset[data[key].id].min = datasets[data[key].id].min;
				CurrentDataset[data[key].id].max = datasets[data[key].id].max;
				data[key].data = datasets[data[key].id].data; 
				data[key].factor = datasets[data[key].id].factor
				plot(key,false,false);
			
				/*$('#placeholderAnalog'+key).unbind('plotpan').bind('plotpan',function(event,plot){
					
					nameKey = plot.getPlaceholder()[0].id.slice(11)
					for (var k in data) {
						if (nameKey == "Analog"+k) {
						key = k;
						break
						}
					}
					xMin[data[key].id] = plot.getAxes().xaxis.min;
					xMax[data[key].id] = plot.getAxes().xaxis.max;
					MinOffset[data[key].id] = plot.getAxes().yaxis.min;
					MaxOffset[data[key].id] = plot.getAxes().yaxis.max;
					jump[data[key].id] = parseInt(xMax[data[key].id]-xMin[data[key].id]);
					if (xMax[data[key].id]+jump[data[key].id] > data[key].data[data[key].data.length-1][0] && xMax[data[key].id]+jump[data[key].id] < dataOverview[key].data.slice(-1)[0][0]) {
						ws.send('newWindow('+JSON.stringify(jump)+',"right", ['+data[key].id+'])')
					} else if(xMin[data[key].id] < 1.1*data[key].data[0][0] && xMin[data[key].id] > 0) {
						ws.send('newWindow('+JSON.stringify(jump)+',"left", ['+data[key].id+'])')
					}
					overviewPlot[key].setSelection({xaxis:{from:xMin[data[key].id],to:xMax[data[key].id]}},true);
				});*/
			}
			
		} else {
			xMin[data[key].id] = datasets[data[key].id].min;
			xMax[data[key].id] = datasets[data[key].id].max;
			overviewPlot[key].setSelection({xaxis:{from:xMin[data[key].id],to:xMax[data[key].id]}},true);
			CurrentDataset[data[key].id].data = datasets[data[key].id].data;
			CurrentDataset[data[key].id].min = datasets[data[key].id].min;
			CurrentDataset[data[key].id].max = datasets[data[key].id].max;
			data[key].data = datasets[data[key].id].data; 
			data[key].factor = datasets[data[key].id].factor
			plot(key,false,false);
			
			/*$('#placeholderAnalog'+key).unbind('plotpan').bind('plotpan',function(event,plot){
					
				nameKey = plot.getPlaceholder()[0].id.slice(11)
				for (var k in data) {
					if (nameKey == "Analog"+k) {
					key = k;
					break
					}
				}
				xMin[data[key].id] = plot.getAxes().xaxis.min;
				xMax[data[key].id] = plot.getAxes().xaxis.max;
				MinOffset[data[key].id] = plot.getAxes().yaxis.min;
				MaxOffset[data[key].id] = plot.getAxes().yaxis.max;
				jump[data[key].id] = parseInt(xMax[data[key].id]-xMin[data[key].id]);
				if (xMax[data[key].id]+jump[data[key].id] > data[key].data[data[key].data.length-1][0] && xMax[data[key].id]+jump[data[key].id] < dataOverview[key].data.slice(-1)[0][0]) {
					ws.send('newWindow('+JSON.stringify(jump)+',"right", ['+data[key].id+'])')
				} else if(xMin[data[key].id] < 1.1*data[key].data[0][0] && xMin[data[key].id] > 0) {
					ws.send('newWindow('+JSON.stringify(jump)+',"left", ['+data[key].id+'])')
				}
				overviewPlot[key].setSelection({xaxis:{from:xMin[data[key].id],to:xMax[data[key].id]}},true);
			});*/
		}
	}
}

function concatData(dtsets, direction) {
	trSelected=$(".graphSelected")
	console.log(dtsets)
	for (var key in data) {
		
		if (trSelected.length > 0){
			if ($("#tr"+data[key].id+"_"+key).attr('class') == 'graphic graphSelected') {
				if (direction == 'right') {
					data[key].data = data[key].data.slice(0).concat(dtsets[data[key].id].data.slice(0));
					
				} else if (direction == 'left') {
					data[key].data = dtsets[data[key].id].data.slice(0).concat(data[key].data.slice(0));
				}

				plot(key,false,false);
			}
			
		} else if (dtsets[data[key].id].data.length > 0){
			
			if (direction == 'right') {
				data[key].data = data[key].data.slice(0).concat(dtsets[data[key].id].data.slice(0));
			} else if (direction == 'left') {
				data[key].data = dtsets[data[key].id].data.slice(0).concat(data[key].data.slice(0));
			}
			plot(key,false,false);
		}
	}
}


function TreeView(Signals,Path) {
	$("#ConfirmCheck").show();
	console.log('Path tree view')
	console.log(Path)
	$("#FilesandFolders").empty();
	/*$("#ConfirmCheck").mouseover(function() {
		$(this).attr({src:'Img/new/certo_azul.png'});
	})
	$("#ConfirmCheck").mouseout(function() {
		$(this).attr({src:'Img/new/certo_cinza.png'});
	})
	
	$("#cancel").mouseover(function() {
		$(this).attr({src:'Img/new/errado_azul.png'});
	})
	$("#cancel").mouseout(function() {
		$(this).attr({src:'Img/new/errado_cinza.png'});
	})
	
	$("#goBack").mouseover(function() {
		$(this).attr({src:'Img/backFhover.png'});
	})
	$("#goBack").mouseout(function() {
		$(this).attr({src:'Img/backF.png'});
	})*/
    $("#goBack").show();	
	S = Signals;
	T=[];
	JSON_FINAL={};
	for (var i in Signals) {
		T[i]=Signals[i].split("/");
		JSON_FINAL = createJSON(JSON_FINAL,T[i])
	}
		
	function createFile(array) {
		l=array.length;
		JSONt = "";
		temp={};
		j=0;
		while (j<l) {
			temp[array[l-j-1]] = JSONt;
			JSONt = temp;
			temp={};
			j++;
		}
		
		return JSONt
	}
	
	function createJSON(jsonp,strArray) {
		if (jsonp[strArray[0]] != undefined) {
			createJSON(jsonp[strArray[0]],strArray.slice(1,strArray.length))
		} else {
			jsonp[strArray[0]] = createFile(strArray.slice(1,strArray.length));
		}
		return jsonp	
	}
	
	for (var keys in JSON_FINAL) {
		JSON_FINAL[keys]
	
	}
	
	//JSON_FINAL = {"signals":{"BVP":{"raw":{"signal0":""},"filtered":{"signal0":""},"filt":{"signal0":""}},"ECG":{"raw":{"signal0":""},"filtered":{"signal0":""}},"EDA":{"raw":{"signal0":""}}}};
	it=0;

	res = jsonToHtmlList(JSON_FINAL)
	function jsonToHtmlList(jsonp) {
    return objToHtmlList(jsonp);
	}

	function objToHtmlList(obj) {
		if (obj instanceof Object) {
			var ul = document.createElement('ul');
			for (var child in obj) {
					var li = document.createElement('li');
					if (obj[child] == "") {
						it++;
						li.innerHTML = '<input type="checkbox" class="checkboxFiles" checked = "checked" id="'+it+'">'+child;
					} else {
						li.innerHTML = '<img src="Img/folder.gif" />'+child;
						
					}
					li.appendChild(objToHtmlList(obj[child]));
					ul.appendChild(li);
			}
			return ul;
		}
		else {
			return document.createTextNode(obj);
		}
	}
	
	$("#FilesandFolders").append('<ul id="browser"><input type="checkbox" checked = "checked" id="selectAll">Select All</ul>')
	
	$("#ConfirmCheck").unbind('click').click(function() {
		$("#containTable").empty();
		var files = new Array();
		$('.checkboxFiles:checked').each(function() {
			var i = $(this).attr('id')
			files.push(S[i-1]);
		});
		if (files.length == 0) {
			$("#popMessage").html("CHOOSE SIGNALS TO OPEN");
			$("#popMessage").show()
		} else{
		console.log(files);
		xMin = [];
		xMax = [];
		MinOffset = [];
		MaxOffset = [];
		ws.send("getDatatoFlot("+JSON.stringify(files)+", 1000,'"+Path+"')")
		TreeFiles = files;
		$("#FileExplorer").fadeOut(100);
		// $("#Loading").fadeOut(100);
		$("#WelcomePage").fadeOut(100);
		$("#MainWelcome").fadeOut(100);
		play = false;
		/*units=[];
		for (x=0;x<files.length;x++) {
			units.push("None");
		}*/
		}
		optionsMenuOpen = false;
	})
	
	$("#goBack").unbind('click').click(function() {
		$("#FilesandFolders").empty();
		console.log('go back')
		console.log(Path)
		ws.send('getFile("'+FinalFile+'",False)');
		/*$("#ConfirmCheck").unbind('mouseover')
		$("#ConfirmCheck").unbind('mouseout')
		$("#cancel").unbind('mouseover')
		$("#cancel").unbind('mouseout')
		$("#goBack").unbind('mouseover')
		$("#goBack").unbind('mouseout')*/
		$("#goBack").fadeOut(100);
	})
	$("#browser").append(res)
	jqtree("#browser").treeview();
	$("#selectAll").click(function(event) {
        if(this.checked) { // check select status
            $('.checkboxFiles').each(function() { //loop through each checkbox
                this.checked = true;  //select all checkboxes with class "checkboxFiles"               
            });
        }else{
            $('.checkboxFiles').each(function() { //loop through each checkbox
                this.checked = false; //deselect all checkboxes with class "checkboxFiles"                       
            });         
        }
    });
	
}

// FUNCTION TO MOVE BOX CONTAINING ANNOTATIONS
function moveBox(key) {
	if (OpenOrClose[key]) {
		$("#content"+data[key].id+"_"+key).css('left','-143px');
		$("#boxContentTable"+data[key].id+"_"+key).fadeOut(200);
		OpenOrClose[key]=false;
	} else {
		$("#content"+data[key].id+"_"+key).css('left','45px');
		$("#boxContentTable"+data[key].id+"_"+key).fadeIn(100);
		OpenOrClose[key]=true;
	}
}
	
function changeYScaleOff(UpOrDown) {
	trSelected=$(".graphSelected")
	
	if (trSelected.length > 0) { //there is a plot selected
		if (UpOrDown == 'up') {
			for (tr=0;tr<trSelected.length;tr++) {
				//keyLabel = trSelected[tr].id.slice(-2,-1)
				keyLabel = trSelected[tr].id.split("_")[0].slice(2)
				i = trSelected[tr].id.split("_")[1]
				if (MaxOffset[keyLabel] < limits[units[data[i].id]][1]) {
					//i = trSelected[tr].id.slice(-1)
					
					MaxOffset[keyLabel]+=(limits[units[data[i].id]][1]-limits[units[data[i].id]][0])*0.005
					MinOffset[keyLabel]+=(limits[units[data[i].id]][1]-limits[units[data[i].id]][0])*0.005
					plot(i,false,false)
				//$.plot($("#placeholderAnalog"+keyLabel),[{data:data[keyLabel].data,color:data[keyLabel].color}],$.extend(true, {}, options, {xaxis:{max:xMax[keyLabel],min:xMin[keyLabel],panRange:[0,data[keyLabel].data[data[keyLabel].data.length-1][0]]},yaxis:{min:MinOffset[keyLabel],max:MaxOffset[keyLabel]}}));
				}
			}
		} else if (UpOrDown == 'down') {
			for (tr=0;tr<trSelected.length;tr++) {
				//keyLabel = trSelected[tr].id.slice(-2,-1)
				keyLabel = trSelected[tr].id.split("_")[0].slice(2)
				i = trSelected[tr].id.split("_")[1]
				if (MinOffset[keyLabel] > limits[units[data[i].id]][0]) {
					//i = trSelected[tr].id.slice(-1)
					
					MaxOffset[keyLabel]-=(limits[units[data[i].id]][1]-limits[units[data[i].id]][0])*0.005
					MinOffset[keyLabel]-=(limits[units[data[i].id]][1]-limits[units[data[i].id]][0])*0.005
					plot(i,false,false)
				}
				// $.plot($("#placeholderAnalog"+keyLabel),[{data:data[keyLabel].data,color:data[keyLabel].color}],$.extend(true, {}, options, {xaxis:{max:xMax[keyLabel],min:xMin[keyLabel],panRange:[0,data[keyLabel].data[data[keyLabel].data.length-1][0]]},yaxis:{min:MinOffset[keyLabel],max:MaxOffset[keyLabel]}}));
			}
		}
		
	} else { // apply changing to all plots
		if (UpOrDown == 'up') {
			for (var i in data) {
				if (MaxOffset[data[i].id] < limits[units[data[i].id]][1]) {
					MaxOffset[data[i].id]+=(limits[units[data[i].id]][1]-limits[units[data[i].id]][0])*0.005;
					MinOffset[data[i].id]+=(limits[units[data[i].id]][1]-limits[units[data[i].id]][0])*0.005;
					plot(i,false,false)
				}
				// $.plot($("#placeholderAnalog"+data[i].id),[{data:data[i].data,color:data[i].color}],$.extend(true, {}, options, {xaxis:{max:xMax[i],min:xMin[i],panRange:[0,data[i].data[data[i].data.length-1][0]]},yaxis:{min:MinOffset[i],max:MaxOffset[i]}}));
			}
			
		} else if (UpOrDown == 'down') {
			for (var i in data) {
				if (MinOffset[data[i].id] > limits[units[data[i].id]][0]) {
					MaxOffset[data[i].id]-=(limits[units[data[i].id]][1]-limits[units[data[i].id]][0])*0.005;
					MinOffset[data[i].id]-=(limits[units[data[i].id]][1]-limits[units[data[i].id]][0])*0.005;
					plot(i,false,false)
				}
				// $.plot($("#placeholderAnalog"+data[i].id),[{data:data[i].data,color:data[i].color}],$.extend(true, {}, options, {xaxis:{max:xMax[i],min:xMin[i],panRange:[0,data[i].data[data[i].data.length-1][0]]},yaxis:{min:MinOffset[i],max:MaxOffset[i]}}));
			}
		}
	}
	
}

function ZoomingOff(InOrOut) {
	trSelected=$(".graphSelected")
	if (trSelected.length > 0) { //there is a plot selected
		if (InOrOut == 'in') { // (+)
			for (tr=0;tr<trSelected.length;tr++) {
				//keyLabel = trSelected[tr].id.slice(-2,-1)
				keyLabel = trSelected[tr].id.split("_")[0].slice(2)
				//i = trSelected[tr].id.slice(-1)
				i = trSelected[tr].id.split("_")[1]
				MaxOffset[keyLabel]-=(limits[units[data[i].id]][1]-limits[units[data[i].id]][0])*0.005
				MinOffset[keyLabel]+=(limits[units[data[i].id]][1]-limits[units[data[i].id]][0])*0.005
				if (MaxOffset[keyLabel]-MinOffset[keyLabel] > (limits[units[data[i].id]][1]-limits[units[data[i].id]][0])*0.005) {
					plot(i,false,false)
				} else {
					MaxOffset[keyLabel]+=(limits[units[data[i].id]][1]-limits[units[data[i].id]][0])*0.005
					MinOffset[keyLabel]-=(limits[units[data[i].id]][1]-limits[units[data[i].id]][0])*0.005
				}
				// $.plot($("#placeholderAnalog"+keyLabel),[{data:data[keyLabel].data,color:data[keyLabel].color}],$.extend(true, {}, options, {xaxis:{max:xMax[keyLabel],min:xMin[keyLabel],panRange:[0,data[keyLabel].data[data[keyLabel].data.length-1][0]]},yaxis:{min:MinOffset[keyLabel],max:MaxOffset[keyLabel]}}));
			}
		} else if (InOrOut == 'out') { // (-)
			for (tr=0;tr<trSelected.length;tr++) {
				//keyLabel = trSelected[tr].id.slice(-2,-1)
				keyLabel = trSelected[tr].id.split("_")[0].slice(2)
				//i = trSelected[tr].id.slice(-1)
				i = trSelected[tr].id.split("_")[1]
				MaxOffset[keyLabel]+=(limits[units[data[i].id]][1]-limits[units[data[i].id]][0])*0.005
				MinOffset[keyLabel]-=(limits[units[data[i].id]][1]-limits[units[data[i].id]][0])*0.005
				plot(i,false,false)
				
				// $.plot($("#placeholderAnalog"+keyLabel),[{data:data[keyLabel].data,color:data[keyLabel].color}],$.extend(true, {}, options, {xaxis:{max:xMax[keyLabel],min:xMin[keyLabel],panRange:[0,data[keyLabel].data[data[keyLabel].data.length-1][0]]},yaxis:{min:MinOffset[keyLabel],max:MaxOffset[keyLabel]}}));
			}
		}
		
	} else { // apply zooming to all plots
		if (InOrOut == 'in') { // (+)
			for (var i in data) {
				MaxOffset[data[i].id]-=(limits[units[data[i].id]][1]-limits[units[data[i].id]][0])*0.005;
				MinOffset[data[i].id]+=(limits[units[data[i].id]][1]-limits[units[data[i].id]][0])*0.005;
				if (MaxOffset[data[i].id]-MinOffset[data[i].id] > (limits[units[data[i].id]][1]-limits[units[data[i].id]][0])*0.005) {
					plot(i,false,false)
				} else {
					MaxOffset[data[i].id]+=(limits[units[data[i].id]][1]-limits[units[data[i].id]][0])*0.005
					MinOffset[data[i].id]-=(limits[units[data[i].id]][1]-limits[units[data[i].id]][0])*0.005
				}
				// $.plot($("#placeholderAnalog"+data[i].id),[{data:data[i].data,color:data[i].color}],$.extend(true, {}, options, {xaxis:{max:xMax[i],min:xMin[i],panRange:[0,data[i].data[data[i].data.length-1][0]]},yaxis:{min:MinOffset[i],max:MaxOffset[i]}}));
			}
			
		} else if (InOrOut == 'out') { // (-)
			for (var i in data) {
				MaxOffset[data[i].id]+=(limits[units[data[i].id]][1]-limits[units[data[i].id]][0])*0.005;
				MinOffset[data[i].id]-=(limits[units[data[i].id]][1]-limits[units[data[i].id]][0])*0.005;
				plot(i,false,false)
				// $.plot($("#placeholderAnalog"+data[i].id),[{data:data[i].data,color:data[i].color}],$.extend(true, {}, options, {xaxis:{max:xMax[i],min:xMin[i],panRange:[0,data[i].data[data[i].data.length-1][0]]},yaxis:{min:MinOffset[i],max:MaxOffset[i]}}));
			}
		}
	}
}

function ChangeXScaleOff(RightOrLeft) {
	trSelected=$(".graphSelected")
	if (trSelected.length > 0) { //there is a plot selected
		if (RightOrLeft == 'right') { // (right)
			channels = []
			for (tr=0;tr<trSelected.length;tr++) {
				//keyLabel = trSelected[tr].id.slice(-2,-1)
				keyLabel = trSelected[tr].id.split("_")[0].slice(2)
				//i = trSelected[tr].id.slice(-1)
				i = trSelected[tr].id.split("_")[1]
				jump[keyLabel] = parseInt(xMax[keyLabel]-xMin[keyLabel])
				// jump = 0.75*jump
				if (xMax[keyLabel]+jump[keyLabel] < data[i].data[data[i].data.length-1][0]) {
					xMax[keyLabel]+=jump[keyLabel]
					xMin[keyLabel]+=jump[keyLabel]
					plot(i,false,false)
					// $.plot($("#placeholderAnalog"+keyLabel),[{data:data[keyLabel].data,color:data[keyLabel].color}],$.extend(true, {}, options, {xaxis:{max:xMax[keyLabel],min:xMin[keyLabel],panRange:[0,CurrentDataset[keyLabel].data[CurrentDataset[keyLabel].data.length-1][0]]},yaxis:{min:MinOffset[keyLabel],max:MaxOffset[keyLabel]}}));
					
					overviewPlot[i].setSelection({xaxis:{from:xMin[keyLabel],to:xMax[keyLabel]}},true);
				} else {
                    dif = xMax[keyLabel]+jump[keyLabel]-data[i].data[data[i].data.length-1][0]
					xMax[keyLabel]+=(jump[keyLabel]-dif)
					xMin[keyLabel]+=(jump[keyLabel]-dif)
					// xMax[keyLabel]+=jump
					// xMin[keyLabel]+=jump
					plot(i,false,false)
					// $.plot($("#placeholderAnalog"+keyLabel),[{data:data[keyLabel].data,color:data[keyLabel].color}],$.extend(true, {}, options, {xaxis:{max:xMax[keyLabel],min:xMin[keyLabel],panRange:[0,CurrentDataset[keyLabel].data[CurrentDataset[keyLabel].data.length-1][0]]},yaxis:{min:MinOffset[keyLabel],max:MaxOffset[keyLabel]}}));
					
					if (xMax[keyLabel] < dataOverview[i].data.slice(-1)[0][0]) {
						channels.push(parseInt(keyLabel))
					}
					overviewPlot[i].setSelection({xaxis:{from:xMin[keyLabel],to:xMax[keyLabel]}},true);
                }
			
			}
			if (channels.length > 0) {
				ws.send('newWindow('+JSON.stringify(jump)+',"right", '+JSON.stringify(channels)+')')
			}
			
		} else if (RightOrLeft == 'left') { // (left)
			channels = []
			for (tr=0;tr<trSelected.length;tr++) {
				
				//keyLabel = trSelected[tr].id.slice(-2,-1)
				keyLabel = trSelected[tr].id.split("_")[0].slice(2)
				//i = trSelected[tr].id.slice(-1)
				i = trSelected[tr].id.split("_")[1]
				jump[keyLabel] = parseInt(xMax[keyLabel]-xMin[keyLabel])
				// jump = 0.75*jump
				if (xMin[keyLabel]-jump[keyLabel] > data[i].data[0][0] ) {
					
					xMax[keyLabel]-=jump[keyLabel]
					xMin[keyLabel]-=jump[keyLabel]
					
					plot(i,false,false)
					// $.plot($("#placeholderAnalog"+keyLabel),[{data:data[keyLabel].data,color:data[keyLabel].color}],$.extend(true, {}, options, {xaxis:{max:xMax[keyLabel],min:xMin[keyLabel],panRange:[0,CurrentDataset[keyLabel].data[CurrentDataset[keyLabel].data.length-1][0]]},yaxis:{min:MinOffset[keyLabel],max:MaxOffset[keyLabel]}}));
					
					overviewPlot[i].setSelection({xaxis:{from:xMin[keyLabel],to:xMax[keyLabel]}},true);
				} else {
                    dif = (xMin[keyLabel]-jump[keyLabel])*(-1)+data[i].data[0][0]
					xMax[keyLabel]-=(jump[keyLabel]-dif)
					xMin[keyLabel]-=(jump[keyLabel]-dif)
					plot(i,false,false)
					if (xMin[keyLabel] > 0) {
						channels.push(parseInt(keyLabel))
					}
					// $.plot($("#placeholderAnalog"+keyLabel),[{data:data[keyLabel].data,color:data[keyLabel].color}],$.extend(true, {}, options, {xaxis:{max:xMax[keyLabel],min:xMin[keyLabel],panRange:[0,CurrentDataset[keyLabel].data[CurrentDataset[keyLabel].data.length-1][0]]},yaxis:{min:MinOffset[keyLabel],max:MaxOffset[keyLabel]}}));
					overviewPlot[i].setSelection({xaxis:{from:xMin[keyLabel],to:xMax[keyLabel]}},true);
                }
			}
			if (channels.length > 0) {
				ws.send('newWindow('+JSON.stringify(jump)+',"left", '+JSON.stringify(channels)+')')
			}
		}
		
	} else { // apply scale to all plots
		if (RightOrLeft == 'right') { // (right)
			channels = []
			for (var i in data) {
				jump[data[i].id] = parseInt(xMax[data[i].id]-xMin[data[i].id])
				// jump = 0.75*jump
				if (xMax[data[i].id]+jump[data[i].id] < data[i].data[data[i].data.length-1][0]) {
					xMax[data[i].id]+=jump[data[i].id]
					xMin[data[i].id]+=jump[data[i].id]
					
					
					plot(i,false,false)
					// $.plot($("#placeholderAnalog"+data[i].id),[{data:data[i].data,color:data[i].color}],$.extend(true, {}, options, {xaxis:{max:xMax[i],min:xMin[i],panRange:[0,data[i].data[data[i].data.length-1][0]]},yaxis:{min:MinOffset[i],max:MaxOffset[i]}}));
					
					overviewPlot[i].setSelection({xaxis:{from:xMin[data[i].id],to:xMax[data[i].id]}},true);
				} else {
					dif = xMax[data[i].id]+jump[data[i].id]-data[i].data[data[i].data.length-1][0]
					xMax[data[i].id]+=(jump[data[i].id]-dif)
					xMin[data[i].id]+=(jump[data[i].id]-dif)
					
					plot(i,false,false)
					
					// $.plot($("#placeholderAnalog"+data[i].id),[{data:data[i].data,color:data[i].color}],$.extend(true, {}, options, {xaxis:{max:xMax[i],min:xMin[i],panRange:[0,data[i].data[data[i].data.length-1][0]]},yaxis:{min:MinOffset[i],max:MaxOffset[i]}}));
					if (xMax[data[i].id] < dataOverview[i].data.slice(-1)[0][0]) {
						channels.push(parseInt(data[i].id))
					}
					overviewPlot[i].setSelection({xaxis:{from:xMin[data[i].id],to:xMax[data[i].id]}},true);
				
				}
				
			}
			if (channels.length > 0) {
				ws.send('newWindow('+JSON.stringify(jump)+',"right", '+JSON.stringify(channels)+')')
			}
			
		} else if (RightOrLeft == 'left') { // (left)
			channels = []
			for (var i in data) {
				jump[data[i].id] = parseInt(xMax[data[i].id]-xMin[data[i].id])
				// jump = 0.75*jump
				if (xMin[data[i].id]-jump[data[i].id] > data[i].data[0][0]) {
					xMax[data[i].id]-=jump[data[i].id]
					xMin[data[i].id]-=jump[data[i].id]
					
					plot(i,false,false)
					// $.plot($("#placeholderAnalog"+data[i].id),[{data:data[i].data,color:data[i].color}],$.extend(true, {}, options, {xaxis:{max:xMax[i],min:xMin[i],panRange:[0,data[i].data[data[i].data.length-1][0]]},yaxis:{min:MinOffset[i],max:MaxOffset[i]}}));
					
					overviewPlot[i].setSelection({xaxis:{from:xMin[data[i].id],to:xMax[data[i].id]}},true);
				} else {
					dif = (xMin[data[i].id]-jump[data[i].id])*(-1)+data[i].data[0][0]
					xMax[data[i].id]-=(jump[data[i].id]-dif)
					xMin[data[i].id]-=(jump[data[i].id]-dif)
					
					plot(i,false,false)
					// $.plot($("#placeholderAnalog"+data[i].id),[{data:data[i].data,color:data[i].color}],$.extend(true, {}, options, {xaxis:{max:xMax[i],min:xMin[i],panRange:[0,data[i].data[data[i].data.length-1][0]]},yaxis:{min:MinOffset[i],max:MaxOffset[i]}}));
					if (xMin[data[i].id] > 0) {
						channels.push(parseInt(data[i].id))
					}
					overviewPlot[i].setSelection({xaxis:{from:xMin[data[i].id],to:xMax[data[i].id]}},true);
				}
			}
			if (channels.length > 0) {
				ws.send('newWindow('+JSON.stringify(jump)+',"left", '+JSON.stringify(channels)+')')
			}
		}
	}
}