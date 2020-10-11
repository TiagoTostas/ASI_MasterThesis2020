// VARIABLES
var ListColors = ["rgb(56,161,192)","rgb(140,185,80)","rgb(221, 177, 0)","rgb(238,117,52)","rgb(197, 26, 26)","#CC0033","rgb(134, 72, 134)","rgb(165, 76, 42)","#006600","rgb(46, 177, 161)","grey","black"]
// var ListColorsAn = ["#FA5858","#FAAC58","rgb(236,219,6)","rgb(169,249,98)","#01DF74","#58ACFA","rgb(148,101,245)","#D358F7","rgb(214,133,135)","brown","#585858"];
var rainbow = new Rainbow()
var ListColorsAn = []
for (i=1;i<21;i++) {
	ListColorsAn.push("#"+rainbow.colourAt(i*5))
}
var limits = {"V":[0,3.3],"mV":[0,3300],"uS":[0,1055744],"lx":[0,66000],"G":[-5.5,5],"None":[0,1024]}
var data=[];
var a = [];
var dataOverview=[];
var choiceContainer;
var connection = false;
var xScale = 10
var Settings
var Devices
var incAn
var play = true
var MaxOffset = [];
var MinOffset = [];
var macAddress
var ch = []
var units = []
var overview;
var CurrentDataset;
var CurrentOverview;
var xmin = 10
var xmax = 0
var optionsMenuOpen = false
var digitalOut = [0,0,0,0]
var BeginApp = true
var samplingRate = 1000
var nSamples = 300
var acquisitionSet = false;
var record = false;
var offline = false;
var xMin = [];
var xMax = [];
var jump = []
var annotationKeys = [];
var annotationKeysJSON = {}
var minSelect;
var maxSelect;
var FinalFile = '""';
var OpenOrClose = [];
var alreadyclicked=false;
var annotating = -1;
var plots = [];
var user = "";
var recordSaved = true;
var playOf = false;
//******************************************************************************************

// MENU OPTIONS
$(function() {
	//Keyboard events
	$(document).keydown(function(e){
		if (!play && $('#Loading').is(':hidden')) {
			if (e.keyCode == 37) {//left arrow pressed (38-up,40-down)
				e.preventDefault();
				if (record){ws.send('changeXScale("up")')}
				else if (e.shiftKey) {
					ws.send('getPreviousData("'+$("#filename").text()+'")')
				} else{ChangeXScaleOff('left');}
			} else if (e.keyCode == 39) { //right arrow pressed
				e.preventDefault();
				if (record){ws.send('changeXScale("down")')}
				else if (e.shiftKey) {
					ws.send('getNextData("'+$("#filename").text()+'")')
				} else {ChangeXScaleOff('right')}
			} else if (e.keyCode == 38) { //up arrow pressed
				e.preventDefault();
				if (record) {
					changeYScale("up")
				} else {
					changeYScaleOff("up")
				}
			} else if (e.keyCode == 40) { //down arrow pressed
				e.preventDefault();
				if (record) {
					changeYScale("down")
				} else {
					changeYScaleOff("down")
				}
				
			} else if (e.keyCode == 187 | e.keyCode == 107) { // zoom in (+)
				if (record) {
					Zooming("in")
				} else {
					ZoomingOff("in")
				}
			} else if (e.keyCode == 189 | e.keyCode == 109) { //zoom out (-)
				if (record) {
					Zooming("out")
				} else {
					ZoomingOff("out")
				}
			} else if (annotationKeysJSON.hasOwnProperty(e.keyCode)) {
				if (record) {
					sample = dataGeral['Analog0'][999][0]
					ws.send('saveEvent('+sample+',"'+annotationKeysJSON[e.keyCode]+'")');
					marks.push({lineWidth: 1,color:'black',xaxis:{from:sample,to:sample},label:String.fromCharCode(e.keyCode)})
				}
			} else if (e.altKey && e.keyCode == 78 && !record  ) {  //Alt-N (for annotation Normal)
				getComment('Normal')
				saveComment()
				$("#CommentBox").fadeIn(500);
				/*setTimeout(function(){
				   $("#CommentBox").fadeOut(500);
				}, 1000);*/
			} else if (e.altKey && e.keyCode == 80 && !record) {  //Alt-P (for annotation Pathology)
				getComment('Pathology')
				saveComment()
				$("#CommentBox").fadeIn(500);
				/*setTimeout(function(){
				   $("#CommentBox").fadeOut(500);
				}, 1000);*/
			}
		} 
	})
	
	
	// Click events
	
	$(document).bind('click',function(e){
		if ($('#Loading').is(':hidden')) {
			// $("#Popup").hide()
			if (alreadyclicked) {
				alreadyclicked=false; // reset
				clearTimeout(alreadyclickedTimeout); // prevent this from happening
				// do what needs to happen on double click. 
				if (e.target.className == "headBox" && $("#tr"+e.target.id.slice(2)).attr('class') == 'graphic') {
					//n = e.target.id.slice(-2,-1)
					n = e.target.id.split("_")[1]
					console.log('Color: '+CurrentDataset[n].color)
					console.log("ID = #tr"+e.target.id.slice(2))
					$("#tr"+e.target.id.slice(2)).addClass('graphSelected')
					$("#tr"+e.target.id.slice(2)).css({'border-top':'1px solid '+CurrentDataset[n].color,'border-bottom':'1px solid '+CurrentDataset[n].color,'border-right':'1px solid '+CurrentDataset[n].color})
					$("#h3"+e.target.id.slice(2)).css({'color':CurrentDataset[n].color})
				} else if (e.target.className == "headBox" && $("#tr"+e.target.id.slice(2)).attr('class') == 'graphic graphSelected') {
					$("#tr"+e.target.id.slice(2)).removeClass('graphSelected')
					$("#tr"+e.target.id.slice(2)).css({'border-top':'1px solid #B1B1B1','border-bottom':'1px solid #B1B1B1','border-right':'1px solid #B1B1B1'})
					$("#h3"+e.target.id.slice(2)).css({'color':'#555'})
				}else {
					$('tr[id]').removeClass('graphSelected')
					$('tr[id]').css({'border-top':'1px solid #B1B1B1','border-bottom':'1px solid #B1B1B1','border-right':'1px solid #B1B1B1'})
					$('h3[id]').css({'color':'#555'})
				}
				
			} else if (!alreadyclicked){
				alreadyclicked=true;
				$('#alreadyclicked').val('clicked');
				alreadyclickedTimeout=setTimeout(function(){
					alreadyclicked=false; // reset when it happens
					if (e.target.className == "headBox") {
						//n = e.target.id.slice(-2,-1)
						n = e.target.id.split("_")[1]
						if (record == false) {
							//open box
							moveBox(n);
							$("#Popup").hide()
						}					
					} else if(e.target.className == "mycheckbox-label") {
						$("#Popup").hide()
						if (JSON.stringify(e.toElement.control.id).search("check") != -1) {
							//key = e.toElement.control.id.slice(5,6);
							key = e.toElement.control.id.split("_")[0].slice(5);
							if ($("#"+e.toElement.control.id).is(':checked')) {
								$("#"+e.toElement.control.id).attr('checked', false);
								plot(key,false,false)
							} else {
								$("#"+e.toElement.control.id).attr('checked', true);
								plot(key,false,false)
							}
						
						} else {
							if (!record) {
								if ($("#"+e.toElement.control.id).is(':checked')) {
									$("#"+e.toElement.control.id).attr('checked', false);
									plotAccordingToChoices()
								} else {
									$("#"+e.toElement.control.id).attr('checked', true);
									plotAccordingToChoices()
								}
							}
						}
					} else if (e.target.id != "comments" && e.target.id !="commentsTitle" && e.target.id != "filename") {
						if( $("#CommentBox").is(':visible') ) {
							$("#CommentBox").fadeOut(100);
							saveComment();
						}
					}
				},200); // <-- dblclick tolerance here
			}
			return false;
		} else if (e.target.id == "MainWelcome" && optionsMenuOpen == false) {
			$("#Loading").fadeOut(100);
			$("#WelcomePage").fadeOut(100)
			$("#MainWelcome").fadeOut(100)
			$("#Popup").hide()
		
		} 
	});
	
	$("#MenuLogo").click(function() {
		$("#Popup").hide()
		if (play == false && record) {
			acquisitionSet = false;
			$("#WelcomePage").fadeIn(100)
			$("#MainWelcome").fadeIn(100)
			$("#Loading").fadeIn(100);
			play = true
			$("#stopArrow").hide();
			// ws.send('StopAcquisition()');
			ws.send('saveDigitalOutput('+JSON.stringify(digitalOut)+')');
			record = false;
			
		} else if(!acquisitionSet) {
			if( $("#CommentBox").is(':visible') ) {
				$("#CommentBox").fadeOut(100);
				saveComment();
			}
			if (annotating != -1) {
				// alert('Save the annotation before choosing other menu options!')
				if (!OpenOrClose[annotating]) {moveBox(annotating);}
				setTimeout(function(){
					divID = "ok"+annotating+"_"+incAn
					popup('top', '<b>Save</b> the annotation before choosing other menu options!', divID, -160, 5)},500);
				
			// } else if (!recordSaved && playOf) { //record not saved previously
				// var r=confirm("Do you want to save this record?");
				
				// if (r==false)
				// {
					// $("#WelcomePage").fadeIn(100)
					// $("#MainWelcome").fadeIn(100)
					// $("#Loading").fadeIn(100);
					// playOf = false;
				// }
				// else
				// {
					// $("#WelcomePage").fadeIn(100)
					// $("#MainWelcome").fadeIn(100)
					// $("#Loading").fadeIn(100);
					// SendDir();
					// $("#ConfirmCheck").unbind('click').click(function() {
						// if ($("#fileName").attr('value') == "") {
							// $("#popMessage").show();
						// }else {
							
							// var path = $('#pathName').attr('value');
							// path = path.replace(/\\/g,"\\\\");
							// var file = $('#fileName').attr('value');
							// type=$("#fileFormat").find(":selected")[0].id
							// ws.send("checkFile('"+path+"','"+file+"','"+type+"')");
						// }
					// })
					// playOf = false;
				// }
			
			
			} else {
				$("#WelcomePage").fadeIn(100)
				$("#MainWelcome").fadeIn(100)
				$("#Loading").fadeIn(100);
				playOf = false;
			}
		}
	})
	

	$("#help").click(function() {
		$("#BackHelp").fadeIn(500);
		optionsMenuOpen = true
	});
	$("#cancel2").click(function() {
		$("#BackHelp").fadeOut(500);
		optionsMenuOpen = false
	})
	$("#cancel2").mouseover(function() {
		$(this).attr({src:'Img/cancelFhover.png'});
	})
	$("#cancel2").mouseout(function() {
		$(this).attr({src:'Img/cancelF.png'});
	})
})

function ConnectionMade() {
	ws.send("getSettings()")
}

// FUNCTION TO CHECK IF CTRL BUTTON IS PRESSED
var ctrlPressed = false;
$(window).keydown(function(evt) {
  if (evt.which == 17) { 
	ctrlPressed = true;
  }
}).keyup(function(evt) {
  if (evt.which == 17) { 
	ctrlPressed = false;
  }
});
var PointsSize;
//------------------------------------------------
// BUILD PAGE FUNCTION
//------------------------------------------------
function BuildPage(datasets, filePath) {
	
	if (filePath == "") {
		$("#fileNameTable").hide();
	} else {
		fName = filePath.split('/')
		$("#filename").html(fName[fName.length-1]);
		$("#fileNameTable").show();
		FinalFile = filePath.replace(/\\/g,"\\");
		console.log(FinalFile);
	}
	var i = 0;
	
    $.each(datasets, function(key, val) {
        val.color = ListColors[i];
        ++i;
		PointsSize=datasets[key].data.length
    });
	
	CurrentDataset = datasets;
	CurrentOverview = JSON.parse(JSON.stringify(datasets));
	//if (CurrentOverview[0].data[CurrentOverview[0].data.length-1][0]/3600 > 60)
	
	choiceContainer = $("#boxOContent");
	choiceContainer.empty()
    $.each(datasets, function(key, val) {
        choiceContainer.append('<input type="checkbox" class="mycheckbox" name="' + key +'" checked="checked" id="id' + key + '">' +
								'<label for="id' + key + '" class="mycheckbox-label" style="background:'+val.color+' no-repeat left bottom;border:1px solid '+val.color+';">'+ 
								'</label><p style="margin:0;display:inline-block;margin-right:30px">'+val.label+'</p>');
    });
	
    // choiceContainer.find("input").click(plotAccordingToChoices);

    plotAccordingToChoices();
	if (record || filePath != "") {
		$("#Loading").fadeOut(100);
	}
	connection = true;
	if (!record) {
		ws.send('getComment()')
	}
	
}
// -----------------------------------
// FUNCTION TO PLOT GRAPHICS ACCORDION TO OVERVIEW CHOICE
// -----------------------------------
function plotAccordingToChoices() {
	datasets = CurrentDataset;
	overviewData = CurrentOverview;
	overviewPlot = [];
	data = [];
	dataOverview = []
	OpenOrClose = [];
	choiceContainer.find("input:checked").each(function () {
		var key = $(this).attr("name");
		if (key && datasets[key])
			data.push(datasets[key]);
			dataOverview.push(overviewData[key])
	});
	data.sort(function(a,b) {
		return a.id - b.id;
	});
	if (!record) {
	xMin = [];
	xMax = [];
	MinOffset = [];
	MaxOffset = [];
	units =[]
	for (k in datasets) {
		if ('units' in datasets[k] && !jQuery.isEmptyObject(datasets[k].units) ) {
			limits["New"+k] = [datasets[k].units.min,datasets[k].units.max]
			units.push("New"+k)
		} else {
			units.push("None");
		}
	}
	}
	
	for (key in data) {
		$("label[for='id"+data[key].id+"']").css({background:data[key].color,color:data[key].color});
	}
	choiceContainer.find("input:not(:checked)").each(function() {
		var key = $(this).attr("name");
		$("label[for='id"+key+"']").css({background:"whiteSmoke",color:"#A2A2A2"});
	});
	$("#containTable").empty();
	
	// OVERVIEW
	var overviewD=[];
	for (var j=0;j<PointsSize;j++){
		overviewD.push([j,0])
	}
	/*for (var key in overviewData) {
		dataOverview.push(overviewData[key])
	}*/
	
	if (dataOverview[0].data[dataOverview[0].data.length-1][0]/60000 < 60) {
		optOverview['xaxis']['timeformat'] = "%M:%S";
	} else {
		options['xaxis']['timeformat'] = "%H:%M:%S";
	}
	$("#overviewColumn").empty();
	
	incV=0;
	for (var key in dataOverview) {
		
		$("#overviewColumn").append('<div id="overview'+incV+'" class="overview" style="z-index:'+incV+'" ></div>');
		if (key == dataOverview.length-1) {
			overviewPlot[incV] = $.plot($("#overview"+incV), [{data:dataOverview[key].data,color:dataOverview[key].color}], $.extend(true, {}, optOverview, {selection:{color:dataOverview[key].color}}));
		} else {
			overviewPlot[incV] = $.plot($("#overview"+incV), [{data:dataOverview[key].data,color:dataOverview[key].color}], $.extend(true, {}, optOverview, {xaxis:{color:"transparent", tickColor:"transparent"},selection:{color:dataOverview[key].color}}));
		}
		incV++;
	}
	$("#overviewColumn").append('<div id="overview" class="overview" style="z-index:'+incV+'"></div>')
	/*opt = {
	series: {
				lines: { show: false},
				points: { show: false },
				shadowSize: 0,
			},
			selection: { mode: "x",color:"#B6B6B6"},
			legend:false,
			xaxis: {show:true, mode:"time",timeformat:"%H:%M:%S",color:"transparent",tickColor:"transparent"},
			yaxis: {show:false},
			grid: {backgroundColor: "transparent" ,borderColor:"transparent",borderWidth:0.5}
	};
	overviewPlot[incV] = $.plot($("#overview"),[overviewD],	opt);*/
	overviewPlot[incV] = $.plot($("#overview"),[overviewD],	$.extend(true, {}, optOverview, {xaxis: {show:true,tickColor:"transparent",color:"transparent"},grid: {backgroundColor: "transparent" ,borderColor:"transparent",borderWidth:0.5},selection:{color:"#B6B6B6"},series: {lines:{show:false}}}));
	
	
	var H;
	if (data.length <=3) {
		H = Math.round(($("#containTable").height()-6-(7*data.length))/data.length);
	} else if (data.length == 4){
		H = Math.round(($("#containTable").height()-6-(7*data.length))/2);
		$("#containTable").append('<tr><td id="cell0"></td><td width="7px"></td><td id="cell1"></td></tr>'+
								'<tr><td id="cell2"></td><td width="7px"></td><td id="cell3"></td></tr>'
								)
	} else {
		H = Math.round(($("#containTable").height()-40)/3);
		// $("#containTable").append('<tr><td id="cell0"></td><td width="7px"></td><td id="cell1"></td></tr>'+
								// '<tr><td id="cell2"></td><td width="7px"></td><td id="cell3"></td></tr>'+
								// '<tr><td id="cell4"></td><td width="7px"></td><td id="cell5"></td></tr>')
		cells = ""
		for (c=0;c<data.length;c++) {
			cells += '<tr><td id="cell'+c+'"></td><td width="7px"></td><td id="cell'+(c+1)+'"></td></tr>';
			c++;
		}
		$("#containTable").append(cells);
	}
	
	var k=0;
	for (var key in data) {
		marks = []
		if (data.length <=3) {
			$("#containTable").append('<tr id="tr'+data[key].id+"_"+key+'" class="graphic" ><td valign="top" align="left" width="50px" >'+
									'<div id="box'+data[key].id+"_"+key+'" class="boxesIndividual" style="height:'+H+'px;">'+
									'<h3 id="h3'+data[key].id+"_"+key+'" class="headBox" style="width:'+H+'px;padding-top:5px;top:'+((H/2)-24)+'px;left:-'+((H/2)-23)+'px;border-top:5px solid '+data[key].color+'">'+data[key].label+'</h3>'+
									'<img id="plus'+data[key].id+"_"+key+'" src="Img/Plus.png" title="Add new annotation" onclick="addAnnotation('+key+');" onmouseover="ChangeImgSrc('+key+',true);" onmouseout="ChangeImgSrc('+key+',false);" width="10px" height="10px" class="addAnnotations" style="display:none;position:absolute;top:15px;left:20px;z-index:9" />'+
									'<div id="content'+data[key].id+"_"+key+'" class="contentBoxes" style="height:'+(H-1)+'px;width:200px;left:-143px">'+
									'<div style="display:block;height:84%;width:80%;top:10%;overflow-y:auto;overflow-x:hidden;position:absolute;">'+
									'<div id="boxContentTable'+data[key].id+"_"+key+'" style="display:table-cell;vertical-align:middle;height:'+((H-1)*(0.80))+'px;padding-left:14%;overflow-y:auto;overflow-x:hidden;width:80%"></div></div>'+
									'</div>'+
									'</div>'+
									'</td>'+
									'<td align="right" valign="middle" width="'+($("#containTable").width()-90)+'px" style="padding-left:5px">'+
									'<div id="placeholderAnalog'+key+'" style="z-index:0;width:'+($("#containTable").width()-90)+'px;height:'+(H-40)+'px;"></div>'+
									'</td><td align="center" valign="top" height="'+H+'"px width="20px" >'+
									'</td></tr><tr><td colspan="3" height="7px"></td></tr>');
			
		} else  if (data.length == 4){
			$("#cell"+key).append('<tr id="tr'+data[key].id+"_"+key+'" class="graphic" ><td valign="top" align="left" width="50px" >'+
									'<div id="box'+data[key].id+"_"+key+'" class="boxesIndividual" style="height:'+H+'px;">'+
									'<h3 id="h3'+data[key].id+"_"+key+'"   class="headBox" style="width:'+H+'px;padding-top:5px;top:'+((H/2)-24)+'px;left:-'+((H/2)-23)+'px;border-top:5px solid '+data[key].color+'">'+data[key].label+'</h3>'+
									'<img id="plus'+data[key].id+"_"+key+'" src="Img/Plus.png" title="Add new annotation" onclick="addAnnotation('+key+');" onmouseover="ChangeImgSrc('+key+',true);" onmouseout="ChangeImgSrc('+key+',false);" width="10px" height="10px" class="addAnnotations" style="display:none;position:absolute;top:15px;left:20px;z-index:9" />'+
									'<div id="content'+data[key].id+"_"+key+'" class="contentBoxes" style="height:'+(H-1)+'px;width:200px;left:-143px">'+
									'<div style="display:block;height:84%;width:80%;top:10%;overflow-y:auto;overflow-x:hidden;position:absolute;">'+
									'<div id="boxContentTable'+data[key].id+"_"+key+'" style="display:table-cell;vertical-align:middle;height:'+((H-1)*(0.80))+'px;padding-left:14%;overflow-y:auto;overflow-x:hidden;width:80%"></div></div>'+
									'</div>'+
									'</div>'+
									'</td>'+
									'<td align="right" height="'+H+'"px valign="middle" style="padding-left:5px">'+
									'<div id="placeholderAnalog'+key+'" style="z-index:0;width:'+(($("#containTable").width()/2)-80)+'px;height:'+(H-40)+'px;"></div>'+
									'</td><td align="center" valign="top" height="'+H+'"px width="10px" >'+
									'</td></tr><tr><td colspan="3" height="7px"></td></tr>');
			
		} else if (data.length >4) {
			$("#cell"+key).append('<tr id="tr'+data[key].id+"_"+key+'" class="graphic" ><td valign="top" align="left" width="50px" >'+
									'<div id="box'+data[key].id+"_"+key+'" class="boxesIndividual" style="height:'+H+'px;">'+
									'<h3 id="h3'+data[key].id+"_"+key+'"   class="headBox" style="width:'+H+'px;padding-top:5px;top:'+((H/2)-24)+'px;left:-'+((H/2)-23)+'px;border-top:5px solid '+data[key].color+'">'+data[key].label+'</h3>'+
									'<img id="plus'+data[key].id+"_"+key+'" src="Img/Plus.png" title="Add new annotation" onclick="addAnnotation('+key+');" onmouseover="ChangeImgSrc('+key+',true);" onmouseout="ChangeImgSrc('+key+',false);" width="10px" height="10px" class="addAnnotations" style="display:none;position:absolute;top:15px;left:20px;z-index:9" />'+
									'<div id="content'+data[key].id+"_"+key+'" class="contentBoxes" style="height:'+(H-1)+'px;width:200px;left:-143px">'+
									'<div style="display:block;height:84%;width:80%;top:10%;overflow-y:auto;overflow-x:hidden;position:absolute;">'+
									'<div id="boxContentTable'+data[key].id+"_"+key+'" style="display:table-cell;vertical-align:middle;height:'+((H-1)*(0.80))+'px;padding-left:14%;overflow-y:auto;overflow-x:hidden;width:80%"></div></div>'+
									'</div>'+
									'</div>'+
									'</td>'+
									'<td align="right" height="'+H+'"px valign="middle" style="padding-left:5px">'+
									'<div id="placeholderAnalog'+key+'" style="z-index:0;width:'+(($("#containTable").width()/2)-80)+'px;height:'+(H-40)+'px;"></div>'+					
									'</td><td align="center" valign="top" height="'+H+'"px width="10px" >'+
									'</td></tr><tr><td colspan="3" height="7px"></td></tr>');
			
			
		}
		var d = [{data:data[key].data,color:data[key].color}];
		OpenOrClose[key]=false;
		if (MaxOffset.length < data.length || record) {
			MaxOffset[data[key].id] = limits[units[data[key].id]][1];
			MinOffset[data[key].id] = limits[units[data[key].id]][0];
			xMin[data[key].id] = 0;
			xMax[data[key].id] = data[key].data[data[key].data.length-1][0];
			jump[data[key].id] = 0;
		}
		if (data[key].anot.length > 0) {
			for (var x in data[key].anot) {
				//$("#boxContentTable"+data[key].label.replace(/\s+/g, '')).append('<input id="check'+key+x+'" type="checkbox" class="mycheckbox" onclick="plot('+key+',false,false);" checked="checked"/>'+
				$("#boxContentTable"+data[key].id+"_"+key).append('<input id="check'+key+"_"+x+'" type="checkbox" class="mycheckbox" checked="checked"/>'+
															'<label id="check2'+key+"_"+x+'" for="check'+key+"_"+x+'" class="mycheckbox-label" style="display:inline-block;margin-bottom:0px; margin-right:3px;background:'+ListColorsAn[x]+';border:1px solid '+ListColorsAn[x]+';color:'+ListColorsAn[x]+'"></label>'+
															// '<input type="text" id="name'+key+x+'" class="inputText" value="'+data[key].anot[x].label+'" disabled="disabled" style="color:'+ListColorsAn[x]+';"/>'+
															'<input type="text" id="name'+key+"_"+x+'" class="inputText" value="'+data[key].anot[x].label+'" disabled="disabled" style="color:black;"/>'+
															'<img id = "edit'+key+"_"+x+'" src="Img/edit.png" onclick="editAnnotation('+key+','+x+')" width="20px" height="20px" style="position:relative;top:2px;left:2px"/>'+
															'<img id ="delete'+key+"_"+x+'" src="Img/trash.png" onclick="deleteAnnotation('+key+','+x+')" width="20px" height="20px" style="position:relative;top:2px;left:2px"/>'+
															'<hr noshade size="1" id="line'+key+"_"+x+'" style="margin: 2px auto 2px auto;border-color:#A7A7A7"/>');
				data[key].anot[x].color = ListColorsAn[x]
				for (var points in data[key].anot[x].data) {
					if (data[key].anot[x].data[points].length != 2) {
						marks.push({ color: data[key].anot[x].color, lineWidth: 1, xaxis: { from: (data[key].anot[x].data[points]), to: (data[key].anot[x].data[points]) } });
					} else {
						marks.push({ color: data[key].anot[x].color, lineWidth: 1, xaxis: { from: (data[key].anot[x].data[points][0]), to: (data[key].anot[x].data[points][1]) } });
					}
					
				}
				
				$("#edit"+key+"_"+x).mouseover(function() {
					$(this).attr({src:'Img/edithover.png'});
				})
				$("#edit"+key+"_"+x).mouseout(function() {
					$(this).attr({src:'Img/edit.png'});
				})
				$("#delete"+key+"_"+x).mouseover(function() {
					$(this).attr({src:'Img/trashhover.png'});
				})
				$("#delete"+key+"_"+x).mouseout(function() {
					$(this).attr({src:'Img/trash.png'});
				})
			}
			plots[key] = $.plot($("#placeholderAnalog"+key),d,$.extend(true, {}, options,{xaxis:{min:xMin[data[key].id], max:xMax[data[key].id],panRange:[data[key].data[0][0],data[key].data[data[key].data.length-1][0]]},yaxis:{min:MinOffset[data[key].id], max:MaxOffset[data[key].id],panRange:[MinOffset[data[key].id],MaxOffset[data[key].id]]},grid:{markings:marks}}))
			
		} else {
			plots[key] = $.plot($("#placeholderAnalog"+key),d,$.extend(true, {}, options, {xaxis:{min:xMin[data[key].id], max:xMax[data[key].id],panRange:[data[key].data[0][0],data[key].data[data[key].data.length-1][0]]},yaxis:{min:MinOffset[data[key].id], max:MaxOffset[data[key].id],panRange:[MinOffset[data[key].id],MaxOffset[data[key].id]]}}));
			
		}
		$("#boxContentTable"+data[key].id+"_"+key).hide();
		$('#placeholderAnalog'+key).unbind('plotpan').bind('plotpan',function(event,plot){
					
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
		});
		if (!record) {
			sec = parseInt((dataOverview[0]['data'][dataOverview[0]['data'].length-1][0])/1000)
			msec = parseInt((((dataOverview[0]['data'][dataOverview[0]['data'].length-1][0])/1000) - sec)*100)
			document.getElementById("timeScale").innerHTML = sec+"."+msec+"s"
			overviewPlot[key].setSelection({xaxis:{from:xMin[data[key].id],to:xMax[data[key].id]}},true);
		}
	}
	//overviewPlot = $.plot($("#overview"),d,optOverview)
	$("#overview").unbind('plotselected').bind("plotselected", function (event, ranges) {
		
		minSelect = ranges.xaxis.from;
		maxSelect = ranges.xaxis.to;
		sec = parseInt((dataOverview[0]['data'][parseInt(maxSelect)][0]-dataOverview[0]['data'][parseInt(minSelect)][0])/1000)
		msec = parseInt((((dataOverview[0]['data'][parseInt(maxSelect)][0]-dataOverview[0]['data'][parseInt(minSelect)][0])/1000) - sec)*100)
		document.getElementById("timeScale").innerHTML = sec+"."+msec+"s"
		channels = []
		trSelected=$(".graphSelected")
		for (k in data) {
			if (trSelected.length > 0){
				if ($("#tr"+data[k].id+"_"+k).attr('class') == 'graphic graphSelected') {
					channels.push(parseInt(data[k].id))
				}
			} else {
				channels.push(parseInt(data[k].id))
			}
		}
		// ws.send('ZoomData('+dataOverview[0]['data'][parseInt(minSelect)][0]+','+dataOverview[0]['data'][parseInt(maxSelect)][0]+')');
		ws.send('ZoomData('+dataOverview[0]['data'][parseInt(minSelect)][0]+','+dataOverview[0]['data'][parseInt(maxSelect)][0]+','+JSON.stringify(channels)+')');
	});
	
	if (!record) {
		$(".addAnnotations").show();
	}
	
}

// FUNCTION TO ROUND NUMBERS TO FLOAT
function round_float(x,n){
  if(!parseInt(n))
  	var n=0;
  if(!parseFloat(x))
  	return false;
  return Math.round(x*Math.pow(10,n))/Math.pow(10,n);
}

// FUNCTION TO CHANGE LOCK IMAGE WHEN PRESSED
function ChangeImgSrc(key,outOver) {
	if (outOver) {$("#plus"+data[key].id+key).attr({
	src:"Img/PlusOver.png",
	});}
	else { $("#plus"+data[key].id+key).attr({
	src:"Img/Plus.png",
	});}
}

// FILE EXPLORER
function DisplayFiles(directories) {
	$("#FileExplorer").fadeIn(200);
	$("#pathName").attr('value',directories.path);
	var dirFiles = directories.dir;
	var filesList = directories.files;
	var ConstructFiles = '<div id = "content"><ul id="selectable" style = "list-style-type:none; text-align:left;margin-top:5px;padding-left:5px;"><p id = "back" style="padding:3px;font-style:normal;color:black;font-size:14px;margin:5px">..</p>';
	for (var i in dirFiles) {
		ConstructFiles += '<p id = "'+dirFiles[i]+'folder" class = "folder">'+dirFiles[i]+'</p>'
	}
	for (var i in filesList) {
		ConstructFiles += '<p id = "'+filesList[i]+'file" class = "file">'+filesList[i]+'</p>'
	}
	ConstructFiles +='</ul></div>'
	$("#FilesandFolders").append(ConstructFiles)
	$( "#FilesandFolders p" ).mouseover(function() {
			if (document.getElementById($(this).attr('id')).className == "folder") {
				$(this).addClass("fileHighlight");
			} else {
				$(this).addClass("fileHighlightBack");
			}
	});
	$( "#FilesandFolders p" ).mouseout(function() {
			if (document.getElementById($(this).attr('id')).className == "folder fileHighlight") {
				$(this).removeClass("fileHighlight");
			} else {
				$(this).removeClass("fileHighlightBack");
			}
	});
	$( ".folder" ).dblclick(function() {
		var dirID = $(this).attr('id');
		var path = $("#pathName").attr('value');
		path = path.replace(/\\/g,"\\\\");
		var dir = document.getElementById(dirID).innerHTML;
		ws.send('getFile(os.path.abspath("'+path+'\\\\'+dir+'"),False)')
		$("#FilesandFolders").empty();
		
	})
	$(".file").dblclick(function() {
		if (offline) {
			var path = $("#pathName").attr('value');
			path = path.replace(/\\/g,"\\\\");
			var fileName = document.getElementById($(this).attr('id')).innerHTML
			var file = path+'\\\\'+fileName
			$("#fileName").html(fileName);
			$("#filename").html(fileName);
			//$("#userName").html(user);
			FinalFile = file;
			//$("#FilesandFolders").empty();
			//get hdf5 tree structure
			console.log(file)
			ws.send('FileTree("'+FinalFile+'")');
		}
		
	
	})
	$("#back").dblclick(function() {
		var path = $("#pathName").attr('value');
		path = path.replace(/\\/g,"\\\\");
		ws.send('getFile(os.path.abspath("'+path+'"),True)')
		$("#FilesandFolders").empty();
	})
	
	$("#cancel").click(function() {
		$("#Popup").hide()
		$("#FileExplorer").fadeOut(100);
		optionsMenuOpen = false
	});
}

$(function() {
	
	$("#instLogos").click( function() {
	
	});
	
	$("#BackDevices").mouseover(function() {
		$(this).attr({src:'Img/backFhover.png'});
	})
	$("#BackDevices").mouseout(function() {
		$(this).attr({src:'Img/backF.png'});
	})
	
	$("#BackDevices2").mouseover(function() {
		$(this).attr({src:'Img/backFhover.png'});
	})
	$("#BackDevices2").mouseout(function() {
		$(this).attr({src:'Img/backF.png'});
	})
	
	
	$("#helpFileExp").mouseover(function() {
		$(this).attr({src:'Img/new/help_pequeno_azul.png'});
	})
	$("#helpFileExp").mouseout(function() {
		$(this).attr({src:'Img/new/help_pequeno_cinza.png'});
	})
	$("#helpFileExp").click(function() {
		// implementar help do file explorer
	})
	$("#search").mouseover(function() {
		$(this).attr({src:'Img/new/search_1.png'});
	})
	$("#search").mouseout(function() {
		$(this).attr({src:'Img/new/search_cinza.png'});
	})
	
	$("#config").mouseover(function() {
		$(this).attr({src:'Img/new/config_1.png'});
	})
	$("#config").mouseout(function() {
		$(this).attr({src:'Img/new/config_cinza.png'});
	})
	
	$("#help").mouseover(function() {
		$(this).attr({src:'Img/new/help_1.png'});
	})
	$("#help").mouseout(function() {
		$(this).attr({src:'Img/new/help_cinza.png'});
	})
	
	$("#ConfirmCheck").mouseover(function() {
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
	
	$("#exit").mouseover(function() {
		$(this).attr({src:'Img/new/off.png'});
	})
	$("#exit").mouseout(function() {
		$(this).attr({src:'Img/new/on.png'});
	})
	
	$("#exit").click(function() {
		exit();
	})
	 

})
function SendDir() {
	if (offline) {
		$("#ConfirmCheck").hide()
	} else {
		$("#ConfirmCheck").show()
	}
	optionsMenuOpen = true
	$("#FilesandFolders").empty();
	$("#boxToFlip").show()
	ws.send('getFile(os.getcwd(),False)');
}


function printMessage(str) {
	console.log(str)
}

function changeCheckboxStyle(id) {
	if ($("#"+id).is(':checked')) {
		$("label[for='"+id+"']").css({"background":"#76c044","border-color":"#76c044"})
	} else {
		$("label[for='"+id+"']").css({"background":"transparent","border-color":"grey"})
	}
}

function FileExists(check) {
	if (check) {
		confirmPopup('top', "<font size='2'>This file already exists. Do you want to <b>replace</b> it?</font>", "ConfirmCheck", -150, 0)
		
		$("#okPopup").unbind('click').click(function() {
			var path = $('#pathName').attr('value');
			path = path.replace(/\\/g,"\\\\");
			var file = $('#fileName').attr('value');
			type=$("#fileFormat").find(":selected")[0].id
			ws.send("saveFile('"+path+"','"+file+"','"+type+"')");
			$("#popMessageSaving").show();
			$("#FileExplorer").fadeOut(200);
			optionsMenuOpen = false
			$("#popMessage").hide();
			$("#Popup").hide()
			recordSaved = true;
		})
		$("#cancelPopup").unbind('click').click(function() {
			$("#Popup").hide()
		})
	} else {
		var path = $('#pathName').attr('value');
		path = path.replace(/\\/g,"\\\\");
		var file = $('#fileName').attr('value');
		type=$("#fileFormat").find(":selected")[0].id
		ws.send("saveFile('"+path+"','"+file+"','"+type+"')");
		$("#popMessageSaving").show();
		$("#FileExplorer").fadeOut(200);
		optionsMenuOpen = false
		$("#popMessage").hide();
		recordSaved = true;
	}

}

function FileSaved() {
	$("#popMessageSaving").hide();
}

function popup(TopOrDown, message, divToAppend, topPos, leftPos) {
	$("#popupButtons").hide()
	$("#popupMessage").html(message)
	$(".popup").removeClass('confirmpopupDOWN').removeClass('confirmpopupTOP')
	if (TopOrDown == "top") {
		$(".popup").removeClass('popupDOWN').addClass('popupTOP')
		//$("#popupMessage").css({'position':'relative'})
	} else {
		$(".popup").removeClass('popupTOP').addClass('popupDOWN')
		//$("#popupMessage").css({'position':'absolute','top':'null','bottom':0})
	}
	t = $("#"+divToAppend).offset().top +topPos
	l = $("#"+divToAppend).offset().left +leftPos
	$(".popup").css({top:t+'px',left:l+'px'})
	$("#Popup").show()

}

function confirmPopup(TopOrDown, message, divToAppend, topPos, leftPos) {

	$("#popupMessage").html(message)
	$(".popup").removeClass('popupDOWN').removeClass('popupTOP')
	if (TopOrDown == "top") {
		$(".popup").removeClass('confirmpopupDOWN').addClass('confirmpopupTOP')
		//$("#popupMessage").css({'position':'relative'})
	} else {
		$(".popup").removeClass('popupTOP').addClass('popupDOWN')
		//$("#popupMessage").css({'position':'absolute','top':'null','bottom':0})
	}
	$("#popupButtons").show()
	t = $("#"+divToAppend).offset().top +topPos
	l = $("#"+divToAppend).offset().left +leftPos
	$(".popup").css({top:t+'px',left:l+'px'})
	$("#Popup").show()

}

function exit() {
	ws.close()
	window.open("", "_self", "");
	window.close();
}

