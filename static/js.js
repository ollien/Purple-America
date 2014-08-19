window.onload = function(){
	var canvas = document.getElementById("main")
	var ctx = canvas.getContext("2d");
	var coords;
	
	
	$.get('/purpleAmerica',function(data){
		console.log("loaded");
		coords = JSON.parse(data)['coords'];
		var width = 0;
		var height = 0;
		for (var i=0; i<coords.length; i++){
			obj = coords[i]['coords']
			for (var j=0; j<obj.length; j++){
				if (obj[j][0]>width){
					width = obj[j][0]
				}
				if (obj[j][1]>height){
					height=obj[j][1]
				}
			}
		}
		canvas.width = width
		canvas.height = height
		for (var i=0; i<coords.length; i++){
			ctx.fillStyle=coords[i]['color']
			obj = coords[i]['coords']
			ctx.beginPath();
			ctx.moveTo(obj[0][0],obj[0][1])
			for (var j=0; j<obj.length; j++){
				ctx.lineTo(obj[j][0],obj[j][1])
			}
			ctx.closePath();
			ctx.fill();
			
		}
		console.log("done");
		
	});
	
	

};
