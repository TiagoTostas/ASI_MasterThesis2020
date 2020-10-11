// Add Annotation
function addAnnotation(key,event,pos,item) {
	if (!OpenOrClose[key]) {moveBox(key);}
	if (annotating == -1) {
		annotating=key;
		edit=false;
		
		a=[];
		regions=[];
		marks=[];
		incAn = data[key].incNumber;
		/*$("#boxContentTable"+data[key].label.replace(/\s+/g, '')).append('<input id="check'+key+incAn+'" type="checkbox" class="mycheckbox" onclick="plot('+key+',false,false);" checked="checked"/>'+
													'<label id="check2'+key+incAn+'" for="check'+key+incAn+'" id="label'+key+incAn+'" "class="mycheckbox-label" style="display:inline-block;margin-bottom:0px; margin-right:3px;background:'+ListColorsAn[incAn]+';border:1px solid '+ListColorsAn[incAn]+';color:'+ListColorsAn[incAn]+'"></label>'+
													// '<input type="text" id="name'+key+incAn+'" placeholder="NAME" class="inputText" style="color:'+ListColorsAn[incAn]+';"/>'+
													'<input type="text" id="name'+key+incAn+'" placeholder="NAME" class="inputText" style="color:black;"/>'+
													'<img id = "ok'+key+incAn+'" src="Img/checkS.png"  align="top" onclick="saveAnnotation('+key+','+incAn+')" width="20px" height="20px" style="position:relative;top:2px;left:2px" />'+
													'<img id ="cancel'+key+incAn+'" src="Img/cancelS.png"  align="top" onclick="cancelAnnotation('+key+','+incAn+')" width="20px" height="20px" style="position:relative;top:2px;left:2px"/>'+
													'<hr noshade size="1" id="line'+key+incAn+'" style="margin: 2px auto 2px auto;border-color:#A7A7A7"/>');*/
		$("#boxContentTable"+data[key].id+"_"+key).append('<input id="check'+key+"_"+incAn+'" type="checkbox" class="mycheckbox" onclick="plot('+key+',false,false);" checked="checked"/>'+
															'<label id="check2'+key+"_"+incAn+'" for="check'+key+"_"+incAn+'" class="mycheckbox-label" style="display:inline-block;margin-bottom:0px; margin-right:3px;background:'+ListColorsAn[incAn]+';border:1px solid '+ListColorsAn[incAn]+';color:'+ListColorsAn[incAn]+'"></label>'+
															// '<input type="text" id="name'+key+x+'" class="inputText" value="'+data[key].anot[x].label+'" disabled="disabled" style="color:'+ListColorsAn[x]+';"/>'+
															'<input type="text" id="name'+key+"_"+incAn+'" placeholder="NAME" class="inputText" style="color:black;"/>'+
															'<img id = "ok'+key+"_"+incAn+'" src="Img/checkS.png"  align="top" onclick="saveAnnotation('+key+','+incAn+')" width="20px" height="20px" style="position:relative;top:2px;left:2px" />'+
															'<img id ="cancel'+key+"_"+incAn+'" src="Img/cancelS.png"  align="top" onclick="cancelAnnotation('+key+','+incAn+')" width="20px" height="20px" style="position:relative;top:2px;left:2px"/>'+
															'<hr noshade size="1" id="line'+key+"_"+incAn+'" style="margin: 2px auto 2px auto;border-color:#A7A7A7"/>');

		var Id = document.getElementById("name"+key+"_"+incAn);
		Id.focus(function() {$(this).css({border:'1px solid black'})});
		$("#ok"+key+"_"+incAn).mouseover(function() {
			$(this).attr({src:'Img/checkShover.png'});
		})
		$("#ok"+key+"_"+incAn).mouseout(function() {
			$(this).attr({src:'Img/checkS.png'});
		})
		$("#cancel"+key+"_"+incAn).mouseover(function() {
			$(this).attr({src:'Img/cancelShover.png'});
		})
		$("#cancel"+key+"_"+incAn).mouseout(function() {
			$(this).attr({src:'Img/cancelS.png'});
		})
		
		//..............................
		
		plot(key,true,true);
		$('#placeholderAnalog'+key).unbind('plotclick').bind('plotclick',function(event,pos,item){
			ClickJson={"event":event,"pos":pos,"item":item}
			
		});
		$('#placeholderAnalog'+key).unbind('plotselected').bind('plotselected',function (event, ranges){
			//min = ranges.xaxis.from;
			//max = ranges.xaxis.to;
			m=[];
			incAn = data[key].incNumber;
			xMax[key] = plots[key].getAxes().xaxis.max;
			xMin[key] = plots[key].getAxes().xaxis.min;
			MaxOffset[key] = plots[key].getAxes().yaxis.max;
			MinOffset[key] = plots[key].getAxes().yaxis.min;

			a.push([parseInt(ranges.xaxis.from),parseInt(ranges.xaxis.to)])
			var checkbox = $("#boxContentTable"+data[key].id+"_"+key).parent().find("input:checkbox");
			for (var x=0;x<checkbox.length;x++) {
				var xx = checkbox[x].id.split("_")[1]
				//var xx = checkbox[x].id.slice(5+(key.toString().length))
				if ($(checkbox[x]).is(":checked") & xx!= incAn) {// check if checkbox is activated or not
					
					$("label[for='check"+key+"_"+xx+"']").css({background:data[key].anot[xx].color,"border-color":data[key].anot[xx].color});
					$("#name"+key+"_"+xx).css({color:"black"});
					for (var points in data[key].anot[xx].data) {
						m.push({ color: data[key].anot[xx].color, lineWidth: 1, xaxis: { from: (data[key].anot[xx].data[points][0]), to: (data[key].anot[xx].data[points][1]) } });
					}
				} else if (xx!= incAn) { //Change checkbox style when not checked
					$("label[for='check"+key+"_"+xx+"']").css({background:"transparent","border-color":"grey"});
					$("#name"+key+"_"+xx).css({color:"#A2A2A2"});
				}
			}
			for (var i in a) {
				m.push(({color:ListColorsAn[incAn],lineWidth: 1, xaxis: { from: (a[i][0]), to: (a[i][1])} }));
			}
			var d = [{data:data[key].data,color:data[key].color}];
			plots[key] = $.plot($("#placeholderAnalog"+key),d,$.extend(true, {}, options, {xaxis:{max:xMax[key],min:xMin[key],panRange:[0,data[key].data[data[key].data.length-1][0]]},yaxis:{max:MaxOffset[key],min:MinOffset[key]},selection: { mode: "x",mouseClick:"right",color:ListColorsAn[incAn]},crosshair: { mode: "x",color:"black",lineWidth:0.5},series: { color: data[key].color },grid: { markings:m,clickable:true ,hoverable:true}}));
		})
		
		$("#placeholderAnalog"+key).unbind("plotunselected").bind("plotunselected", function(ev) {
			console.log('enter plotclick')
			event = ClickJson.event 
			pos = ClickJson.pos
			item = ClickJson.item
			m=[];
			if (ctrlPressed) { //to delete points or regions
				//ctrlPressed = false;
				if (item) {
					var xPOS = [item.datapoint[0],item.datapoint[0]];
				} else {
					var xPOS = [parseInt(pos.x),parseInt(pos.x)];
				}
				
				var a1=a.slice(0);
				var eliminatePositions = []
				for (var index in a1) {
					// a1[index][0] = Math.round(a1[index][0])
					// a1[index][1] = Math.round(a1[index][1])
					if (xPOS[0] >= a[index][0]-5 & xPOS[1] <= a[index][1]+5) {
						eliminatePositions.push(index);
						console.log("Position to eliminate: " + index);
					}
				}
				for (var i = eliminatePositions.length - 1; i >= 0; i--) {
					a.splice(eliminatePositions[i],1)
				}
				var checkbox = $("#boxContentTable"+data[key].id+"_"+key).parent().find("input:checkbox");
				for (var x=0;x<checkbox.length;x++) {
					var xx = checkbox[x].id.split("_")[1]
					if ($(checkbox[x]).is(":checked") & xx!= incAn) {// check if checkbox is activated or not
						
						$("label[for='check"+key+"_"+xx+"']").css({background:data[key].anot[xx].color,"border-color":data[key].anot[xx].color});
						$("#name"+key+"_"+xx).css({color:"black"});
						for (var points in data[key].anot[xx].data) {
							m.push({ color: data[key].anot[xx].color, lineWidth: 1, xaxis: { from: (data[key].anot[xx].data[points][0]), to: (data[key].anot[xx].data[points][1]) } });
						}
					}else if (xx!= incAn){ //Change checkbox style when not checked
						$("label[for='check"+key+"_"+xx+"']").css({background:"transparent","border-color":"grey"});
						$("#name"+key+"_"+xx).css({color:"#A2A2A2"});
					}
				}
				for (var i in a) {
					m.push(({color:ListColorsAn[incAn],lineWidth: 1, xaxis: { from: (a[i][0]), to: (a[i][1])} }));
				}
				var d = [{data:data[key].data,color:data[key].color}];
				xMax[key] = plots[key].getAxes().xaxis.max;
				xMin[key] = plots[key].getAxes().xaxis.min;
				MaxOffset[key] = plots[key].getAxes().yaxis.max;
				MinOffset[key] = plots[key].getAxes().yaxis.min;
				plots[key] = $.plot($("#placeholderAnalog"+key),d,$.extend(true, {}, options, {xaxis:{max:xMax[key],min:xMin[key],panRange:[0,data[key].data[data[key].data.length-1][0]]},yaxis:{max:MaxOffset[key],min:MinOffset[key]},selection: { mode: "x",mouseClick:"right",color:ListColorsAn[incAn]},crosshair: { mode: "x",color:"black",lineWidth:0.5},series: { color: data[key].color },grid: { markings:m,clickable:true ,hoverable:true}}));
				
			} else { // add new point or region
				incAn = data[key].incNumber;
				xMax[key] = plots[key].getAxes().xaxis.max;
				xMin[key] = plots[key].getAxes().xaxis.min;
				MaxOffset[key] = plots[key].getAxes().yaxis.max;
				MinOffset[key] = plots[key].getAxes().yaxis.min;
				if (item) {
					var xPOS = [item.datapoint[0],item.datapoint[0]];
				} else {
					var xPOS = [parseInt(pos.x),parseInt(pos.x)];
				}
				if (jQuery.inArray(xPOS,a) == -1) {
					a.push(xPOS);
					var checkbox = $("#boxContentTable"+data[key].id+"_"+key).parent().find("input:checkbox");
					for (var x=0;x<checkbox.length;x++) {
						var xx = checkbox[x].id.split("_")[1]
						if ($(checkbox[x]).is(":checked") & xx!= incAn) {// check if checkbox is activated or not
							
							$("label[for='check"+key+"_"+xx+"']").css({background:data[key].anot[xx].color,"border-color":data[key].anot[xx].color});
							$("#name"+key+"_"+xx).css({color:"black"});
							for (var points in data[key].anot[xx].data) {
								m.push({ color: data[key].anot[xx].color, lineWidth: 1, xaxis: { from: (data[key].anot[xx].data[points][0]), to: (data[key].anot[xx].data[points][1]) } });
							}
						} else if (xx != incAn) { //Change checkbox style when not checked
							$("label[for='check"+key+"_"+xx+"']").css({background:"transparent","border-color":"grey"});
							$("#name"+key+"_"+xx).css({color:"#A2A2A2"});
						}
					}
					for (var i in a) {
						m.push(({color:ListColorsAn[incAn],lineWidth: 1, xaxis: { from: (a[i][0]), to: (a[i][1])} }));
					}
					var d = [{data:data[key].data,color:data[key].color}];
					plots[key] = $.plot($("#placeholderAnalog"+key),d,$.extend(true, {}, options, {xaxis:{max:xMax[key],min:xMin[key],panRange:[0,data[key].data[data[key].data.length-1][0]]},yaxis:{max:MaxOffset[key],min:MinOffset[key]},selection: { mode: "x",mouseClick:"right",color:ListColorsAn[incAn]},crosshair: { mode: "x",color:"black",lineWidth:0.5},series: { color: data[key].color },grid: { markings:m,clickable:true ,hoverable:true}}));
				}
			}
			
		})
	
	} else {
		// alert('Save or cancel the last annotation before adding a new one!')
		// console.log($("#content"+data[annotating].label.replace(/\s+/g, '')).position().left)
		
		setTimeout(function(){
			divID = "ok"+annotating+"_"+incAn
			popup('top', '<b>Save/Cancel</b> last annotation before adding a new one!', divID, -160, 5)},500);
	}
}

//Save Annotation
function saveAnnotation(key,annotation) {
	$("#Popup").hide()
	if ($("#name"+key+"_"+annotation).attr('value') == "") {
		// alert('Insert the annotation name before saving.')
		divID = "name"+key+"_"+annotation
		popup('top', 'Insert the annotation <b>name</b> before saving.', divID, -160, 0)
	} 
	else {
		repeatAnot = false;
		// Check if annotation name already exists
		for (anotIndex in data[key].anot) {
			if (anotIndex != annotation && data[key].anot[anotIndex].label == $("#name"+key+"_"+annotation).attr('value') ) {
				repeatAnot = true;
			}
		}
		if (repeatAnot) {
			divID = "name"+key+"_"+annotation
			popup('top', 'This annotation <b>name</b> already exists!', divID, -160, 0)
		} else {
			$("#ok"+key+"_"+annotation).unbind('mouseover');
			$("#ok"+key+"_"+annotation).unbind('mouseout');
			$("#cancel"+key+"_"+annotation).unbind('mouseover');
			$("#cancel"+key+"_"+annotation).unbind('mouseout');
			annotating=-1;
			//$("#placeholder"+data[key].label).unbind('plotpan');
			$("#placeholderAnalog"+key).unbind('plotclick');
			$("#placeholderAnalog"+key).unbind('plotunselected');
			$("#placeholderAnalog"+key).unbind('plotselected');
			$("#name"+key+"_"+annotation).attr('disabled',"disabled");
			$("#ok"+key+"_"+annotation).attr({
			id:"edit"+key+"_"+annotation,
			src:"Img/edit.png",
			});
			document.getElementById("edit"+key+"_"+annotation).onclick = function (){editAnnotation(key,annotation)};
			$("#cancel"+key+"_"+annotation).attr({
			id:"delete"+key+"_"+annotation,
			src:"Img/trash.png",
			});
			document.getElementById("delete"+key+"_"+annotation).onclick = function (){deleteAnnotation(key,annotation)};
			$("#edit"+key+"_"+annotation).mouseover(function() {
				$(this).attr({src:'Img/edithover.png'});
			})
			$("#edit"+key+"_"+annotation).mouseout(function() {
				$(this).attr({src:'Img/edit.png'});
			})
			$("#delete"+key+"_"+annotation).mouseover(function() {
				$(this).attr({src:'Img/trashhover.png'});
			})
			$("#delete"+key+"_"+annotation).mouseout(function() {
				$(this).attr({src:'Img/trash.png'});
			})
			if (edit) { 
				data[key].anot[annotation].data = a.slice(0);
				ws.send("editAnnotations('"+FinalFile+"','line/region','"+JSON.stringify(a.slice(0))+"','"+data[key].path+"','"+data[key].anot[annotation].color+"','"+$("#name"+key+"_"+annotation).attr("value")+"','"+data[key].anot[annotation].label+"','"+user+"')");
				data[key].anot[annotation].label = $("#name"+key+"_"+annotation).attr("value");
			}
			else{
				data[key].anot.push({label:$("#name"+key+"_"+annotation).attr("value"),data:a.slice(0),color:ListColorsAn[annotation]});
				// ws.send('saveAnnotations("'+FinalFile+'","line/region","['+a.slice(0)+']","'+data[key].path+'","'+ListColorsAn[annotation]+'","'+$("#name"+key+annotation).attr("value")+'")')
				ws.send("saveAnnotations('"+FinalFile+"','line/region','"+JSON.stringify(a.slice(0))+"','"+data[key].path+"','"+ListColorsAn[annotation]+"','"+$("#name"+key+"_"+annotation).attr("value")+"','"+user+"')")
				data[key].incNumber = data[key].incNumber+1;
				}
			//if ($("#content"+data[key].label).position().left != (-130)) {moveBox(key);}
			plot(key,false,false);
			edit=false;
			
		}
	}
}

// Cancel Annotation
function cancelAnnotation(key,annotation) {
	$("#Popup").hide();
	//$("#placeholder"+data[key].label).unbind('plotpan');
	$("#placeholderAnalog"+key).unbind('plotclick');
	$("#placeholderAnalog"+key).unbind('plotunselected');
	$("#placeholderAnalog"+key).unbind('plotselected');
	$("#label"+key+"_"+annotation).remove();
	$("#check"+key+"_"+annotation).remove();
	$("#check2"+key+"_"+annotation).remove();
	$("#name"+key+"_"+annotation).remove();
	$("#ok"+key+"_"+annotation).remove();
	$("#cancel"+key+"_"+annotation).remove();
	$("#line"+key+"_"+annotation).remove();
	a=[];
	annotating=-1;
	marks=[];
	plot(key,false,false)
	edit=false;
}

function cancelEdit(key,annotation) {
	$("#Popup").hide();
	//$("#placeholder"+data[key].label).unbind('plotpan');
	$("#placeholderAnalog"+key).unbind('plotclick');
	$("#placeholderAnalog"+key).unbind('plotselected');
	$("#placeholderAnalog"+key).unbind('plotunselected');
	$("#ok"+key+"_"+annotation).unbind('mouseover');
	$("#ok"+key+"_"+annotation).unbind('mouseout');
	$("#cancel"+key+"_"+annotation).unbind('mouseover');
	$("#cancel"+key+"_"+annotation).unbind('mouseout');
	document.getElementById("name"+key+"_"+annotation).disabled=true;
	$("#name"+key+"_"+annotation).val(data[key].anot[annotation].label)
	$("#ok"+key+"_"+annotation).attr({
		id:"edit"+key+"_"+annotation,
		src:"Img/edit.png",
	});
	document.getElementById("edit"+key+"_"+annotation).onclick = function (){editAnnotation(key,annotation)};
	$("#cancel"+key+"_"+annotation).attr({
		id:"delete"+key+"_"+annotation,
		src:"Img/trash.png",
	});
	document.getElementById("delete"+key+"_"+annotation).onclick = function (){
		deleteAnnotation(key,annotation)
	};
	$("#edit"+key+"_"+annotation).mouseover(function() {
		$(this).attr({src:'Img/edithover.png'});
	})
	$("#edit"+key+"_"+annotation).mouseout(function() {
		$(this).attr({src:'Img/edit.png'});
	})
	$("#delete"+key+"_"+annotation).mouseover(function() {
		$(this).attr({src:'Img/trashhover.png'});
	})
	$("#delete"+key+"_"+annotation).mouseout(function() {
		$(this).attr({src:'Img/trash.png'});
	})
	edit=false;
	a=[];
	annotating=-1;
	plot(key,false,false);
}
var edit=false;
// Edit Annotation
function editAnnotation(key,annotation) {
	if (annotating == -1) {
		a=[];
		regions=[];
		edit = true;
		annotating=key;
		incAn = annotation
		a=data[key].anot[annotation].data.slice(0);
		plot(key,true,true);
		document.getElementById("name"+key+"_"+annotation).disabled=false;
		$("#edit"+key+"_"+annotation).attr({
			id:"ok"+key+"_"+annotation,
			src:"Img/checkS.png",
		});
		document.getElementById("ok"+key+"_"+annotation).onclick = function (){saveAnnotation(key,annotation)};
		$("#delete"+key+"_"+annotation).attr({
			id:"cancel"+key+"_"+annotation,
			src:"Img/cancelS.png",
		});
		$("#ok"+key+"_"+annotation).mouseover(function() {
			$(this).attr({src:'Img/checkShover.png'});
		})
		$("#ok"+key+"_"+annotation).mouseout(function() {
			$(this).attr({src:'Img/checkS.png'});
		})
		$("#cancel"+key+"_"+annotation).mouseover(function() {
			$(this).attr({src:'Img/cancelShover.png'});
		})
		$("#cancel"+key+"_"+annotation).mouseout(function() {
			$(this).attr({src:'Img/cancelS.png'});
		})
		document.getElementById("cancel"+key+"_"+annotation).onclick = function (){cancelEdit(key,annotation)};
		
		$("#placeholderAnalog"+key).bind('plotclick',function(event,pos,item){
			ClickJson={"event":event,"pos":pos,"item":item}
		});
		$("#placeholderAnalog"+key).unbind('plotselected').bind('plotselected',function (event, ranges){
			m=[];
			xMax[key] = plots[key].getAxes().xaxis.max;
			xMin[key] = plots[key].getAxes().xaxis.min;
			MaxOffset[key] = plots[key].getAxes().yaxis.max;
			MinOffset[key] = plots[key].getAxes().yaxis.min;

			a.push([parseInt(ranges.xaxis.from),parseInt(ranges.xaxis.to)])
			// plot(key,false,false)
			var checkbox = $("#boxContentTable"+data[key].id+"_"+key).parent().find("input:checkbox");
			for (var x=0;x<checkbox.length;x++) {
				var xx = checkbox[x].id.split("_")[1]
				if ($(checkbox[x]).is(":checked") & xx!= annotation) {// check if checkbox is activated or not
					
					$("label[for='check"+key+"_"+xx+"']").css({background:data[key].anot[xx].color,"border-color":data[key].anot[xx].color});
					$("#name"+key+"_"+xx).css({color:"black"});
					for (var points in data[key].anot[xx].data) {
						m.push({ color: data[key].anot[xx].color, lineWidth: 1, xaxis: { from: (data[key].anot[xx].data[points][0]), to: (data[key].anot[xx].data[points][1]) } });
					}
				} else if(xx!= annotation) { //Change checkbox style when not checked
					$("label[for='check"+key+"_"+xx+"']").css({background:"transparent","border-color":"grey"});
					$("#name"+key+"_"+xx).css({color:"#A2A2A2"});
				}
			}
			for (var i in a) {
				m.push(({color:data[key].anot[annotation].color,lineWidth: 1, xaxis: { from: (a[i][0]), to: (a[i][1])} }));
			}
			var d = [{data:data[key].data,color:data[key].color}];
			plots[key] = $.plot($("#placeholderAnalog"+key),d,$.extend(true, {}, options, {xaxis:{max:xMax[key],min:xMin[key],panRange:[0,data[key].data[data[key].data.length-1][0]]},yaxis:{max:MaxOffset[key],min:MinOffset[key]},selection: { mode: "x",mouseClick:"right",color:data[key].anot[annotation].color},crosshair: { mode: "x",color:"black",lineWidth:0.5},series: { color: data[key].color },grid: { markings:m,clickable:true ,hoverable:true}}));
			
		})
		
				
		$("#placeholderAnalog"+key).unbind('plotunselected').bind("plotunselected", function(ev) {
			console.log('enter plotclick')
			event = ClickJson.event 
			pos = ClickJson.pos
			item = ClickJson.item
			
			m=[];
			if (ctrlPressed) { //to delete points or regions
				//ctrlPressed = false;
				if (item) {
					var xPOS = [item.datapoint[0],item.datapoint[0]];
				} else {
					var xPOS = [parseInt(pos.x),parseInt(pos.x)];
				}
				
				var a1=a.slice(0);
				var eliminatePositions = []
				for (var index in a1) {
					// a1[index][0] = Math.round(a1[index][0])
					// a1[index][1] = Math.round(a1[index][1])
					if (xPOS[0] >= a[index][0]-5 & xPOS[1] <= a[index][1]+5) {
						eliminatePositions.push(index);
						console.log("Position to eliminate: " + index);
					}
				}
				for (var i = eliminatePositions.length - 1; i >= 0; i--) {
					a.splice(eliminatePositions[i],1)
				}
				var checkbox = $("#boxContentTable"+data[key].id+"_"+key).parent().find("input:checkbox");
				for (var x=0;x<checkbox.length;x++) {
					var xx = checkbox[x].id.split("_")[1]
					if ($(checkbox[x]).is(":checked") & xx!= annotation) {// check if checkbox is activated or not
						
						$("label[for='check"+key+"_"+xx+"']").css({background:data[key].anot[xx].color,"border-color":data[key].anot[xx].color});
						$("#name"+key+"_"+xx).css({color:"black"});
						for (var points in data[key].anot[xx].data) {
							m.push({ color: data[key].anot[xx].color, lineWidth: 1, xaxis: { from: (data[key].anot[xx].data[points][0]), to: (data[key].anot[xx].data[points][1]) } });
						}
					}else if (xx!= annotation) { //Change checkbox style when not checked
						$("label[for='check"+key+"_"+xx+"']").css({background:"transparent","border-color":"grey"});
						$("#name"+key+"_"+xx).css({color:"#A2A2A2"});
					}
				}
				for (var i in a) {
					m.push(({color:data[key].anot[annotation].color,lineWidth: 1, xaxis: { from: (a[i][0]), to: (a[i][1])} }));
				}
				var d = [{data:data[key].data,color:data[key].color}];
				xMax[key] = plots[key].getAxes().xaxis.max;
				xMin[key] = plots[key].getAxes().xaxis.min;
				MaxOffset[key] = plots[key].getAxes().yaxis.max;
				MinOffset[key] = plots[key].getAxes().yaxis.min;
				plots[key] = $.plot($("#placeholderAnalog"+key),d,$.extend(true, {}, options, {xaxis:{max:xMax[key],min:xMin[key],panRange:[0,data[key].data[data[key].data.length-1][0]]},yaxis:{max:MaxOffset[key],min:MinOffset[key]},selection: { mode: "x",mouseClick:"right",color:data[key].anot[annotation].color},crosshair: { mode: "x",color:"black",lineWidth:0.5},series: { color: data[key].color },grid: { markings:m,clickable:true ,hoverable:true}}));
				
			} else { // add new point or region
				// incAn = data[key].incNumber;
				xMax[key] = plots[key].getAxes().xaxis.max;
				xMin[key] = plots[key].getAxes().xaxis.min;
				MaxOffset[key] = plots[key].getAxes().yaxis.max;
				MinOffset[key] = plots[key].getAxes().yaxis.min;
				if (item) {
					var xPOS = [item.datapoint[0],item.datapoint[0]];
				} else {
					var xPOS = [parseInt(pos.x),parseInt(pos.x)];
				}
				if (jQuery.inArray(xPOS,a) == -1) {
					a.push(xPOS);
					var checkbox = $("#boxContentTable"+data[key].id+"_"+key).parent().find("input:checkbox");
					for (var x=0;x<checkbox.length;x++) {
						var xx = checkbox[x].id.split("_")[1]
						if ($(checkbox[x]).is(":checked") & xx!= annotation) {// check if checkbox is activated or not
							
							$("label[for='check"+key+"_"+xx+"']").css({background:data[key].anot[xx].color,"border-color":data[key].anot[xx].color});
							$("#name"+key+"_"+xx).css({color:"black"});
							for (var points in data[key].anot[xx].data) {
								m.push({ color: data[key].anot[xx].color, lineWidth: 1, xaxis: { from: (data[key].anot[xx].data[points][0]), to: (data[key].anot[xx].data[points][1]) } });
							}
						} else if(xx!= annotation) { //Change checkbox style when not checked
							$("label[for='check"+key+"_"+xx+"']").css({background:"transparent","border-color":"grey"});
							$("#name"+key+"_"+xx).css({color:"#A2A2A2"});
						}
					}
					for (var i in a) {
						m.push(({color:data[key].anot[annotation].color,lineWidth: 1, xaxis: { from: (a[i][0]), to: (a[i][1])} }));
					}
					var d = [{data:data[key].data,color:data[key].color}];
					plots[key] = $.plot($("#placeholderAnalog"+key),d,$.extend(true, {}, options, {xaxis:{max:xMax[key],min:xMin[key],panRange:[0,data[key].data[data[key].data.length-1][0]]},yaxis:{max:MaxOffset[key],min:MinOffset[key]},selection: { mode: "x",mouseClick:"right",color:data[key].anot[annotation].color},crosshair: { mode: "x",color:"black",lineWidth:0.5},series: { color: data[key].color },grid: { markings:m,clickable:true ,hoverable:true}}));
				}
			}
			
		})
	} else {
		// alert('You can only edit one annotation at a time.')
		if ($("[id^=ok][id!=okPopup]").length > 0) {
			divID = $("[id^=ok][id!=okPopup]").attr('id')
			popup('top', 'You can only edit <b>one</b> annotation at a time.', divID, -160, 5)
		}
	}
}

//Delete Annotation
/*function deleteAnnotation(key,annotation) {
	divID = "delete"+key+"_"+annotation
	confirmPopup('top', "Are you sure you want to <b>delete</b> this annotation?", divID, -160, -15)
		
	$("#okPopup").unbind('click').click(function() {
		for (var ann in data[key].anot){
			if ($("#name"+key+"_"+annotation).attr('value') == data[key].anot[ann].label) {
				ws.send("deleteAnnotations('"+FinalFile+"','"+data[key].path+"','"+data[key].anot[ann].label+"')")
				ListColorsAn.splice(data[key].incNumber,0,data[key].anot[ann].color)
				data[key].anot.splice(ann,1);
				//annotating=-1;
				$("#label"+key+"_"+annotation).remove();
				$("#check"+key+"_"+annotation).remove();
				$("#check2"+key+"_"+annotation).remove();
				$("#name"+key+"_"+annotation).remove();
				$("#edit"+key+"_"+annotation).remove();
				$("#delete"+key+"_"+annotation).remove();
				$("#line"+key+"_"+annotation).remove();
				if (annotating == -1) {plot(key,false,false);}
				else {plot(key,true,true);}
			}
		}
		$("#Popup").hide()
	})
	
	$("#cancelPopup").unbind('click').click(function() {
		$("#Popup").hide()
	})
}*/

function deleteAnnotation(key,annotation) {
	divID = "delete"+key+"_"+annotation
	confirmPopup('top', "Are you sure you want to <b>delete</b> this annotation?", divID, -160, -15)
		
	$("#okPopup").unbind('click').click(function() {
		ws.send("deleteAnnotations('"+FinalFile+"','"+data[key].path+"','"+data[key].anot[annotation].label+"')")
		ListColorsAn.splice(data[key].incNumber,0,data[key].anot[annotation].color)
		data[key].anot[annotation].data = [];
		//annotating=-1;
		if (annotating == -1) {plot(key,false,false);}
		else {plot(key,true,true);}
		$("#label"+key+"_"+annotation).remove();
		$("#check"+key+"_"+annotation).remove();
		$("#check2"+key+"_"+annotation).remove();
		$("#name"+key+"_"+annotation).remove();
		$("#edit"+key+"_"+annotation).remove();
		$("#delete"+key+"_"+annotation).remove();
		$("#line"+key+"_"+annotation).remove();
		

		$("#Popup").hide()
	})
	
	$("#cancelPopup").unbind('click').click(function() {
		$("#Popup").hide()
	})
}
