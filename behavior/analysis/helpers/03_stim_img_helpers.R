library(tidyverse)
library(here)
library(magick)
library(grid)
library(gridExtra)


convertFVToHEX = function(fillingVal){

  if (is.na(fillingVal)){
    hex_code = NA
  } else {
    bothCol = matrix(data = c(.1 , .1, .4, -99, .4, .1, .1, -99), byrow=T, nrow=2, ncol=4)

    if(fillingVal>=0){
      colorStim = bothCol[1,]
      colorStim[3] = ifelse(abs(fillingVal)==.4, .6, ifelse(abs(fillingVal)==.6,.5, ifelse(abs(fillingVal)==.85, .3, colorStim[3])))

    } else{
      colorStim = bothCol[2,]
      colorStim[1] = ifelse(abs(fillingVal)==.4, .6, ifelse(abs(fillingVal)==.6,.5, ifelse(abs(fillingVal)==.85, .3, colorStim[1])))
    }

    colorStim[4] = abs(fillingVal)

    hex_code = rgb(colorStim[1], colorStim[2], colorStim[3], colorStim[4])
  }

  return(hex_code)
}

make_stim_img = function(shape, orientation, filling){

  blank = image_blank(width = 800, height = 800, color = "none")

  # Needs to be run in terminal or all at one in the chunk
  img = image_draw(blank)

  bg_hex = convertFVToHEX(filling)

  symbols(400, 400, circles = 200, bg = bg_hex, inches = FALSE, add = TRUE, lwd = 6)

  bg_circle = image_read(image_write(img))


  shape_img = image_read(paste0('/Users/zeynepenkavi/Downloads/alldata/data_task/pilot5_fmri_1/task_scan/shapes/shape', shape, '.png'))

  tilted_nofill_img = shape_img %>%
    image_background("none") %>%
    image_scale("200") %>%
    image_rotate(orientation)

  tilted_nofill_img = image_read(image_write(tilted_nofill_img))

  offset_x = 200 + (200 - (image_info(tilted_nofill_img)$width/2))
  offset_y = 200 + (200 - (image_info(tilted_nofill_img)$height/2))
  inset_offset = paste0('+', offset_x, '+', offset_y)
  stim_img = image_composite(bg_circle,  tilted_nofill_img, operator = "Over", offset = inset_offset)

  return(stim_img)

}

img_read_border_annotate = function(img_fn, annot_img=TRUE, border_img=TRUE){
  img = image_read(img_fn)

  if(grepl('ht', img_fn) & (border_img)){
    img = image_border(img,"black","1x1")

    # Remove HT from image file name for annotation
    img_fn = paste0(strsplit(img_fn, "_")[[1]][1], '.png')
  }

  if(annot_img){

    cur_sub = as.numeric(strsplit(strsplit(img_fn, "/")[[1]][11], "-")[[1]][2])
    cur_stimNum = as.numeric(strsplit(strsplit(img_fn, "/")[[1]][12], '\\.')[[1]][1])

    cur_stimDat = data_yn_clean %>%
      filter((subnum == cur_sub) & (stimNum == cur_stimNum)) %>%
      select(orientation, filling, shape, valueO, valueF, valueS) %>%
      distinct() %>%
      mutate(meanPayoff = round(100 * ((valueS + valueO + valueF)/2) ))

    cur_shape = cur_stimDat$shape
    cur_orient = cur_stimDat$orientation
    cur_filling = cur_stimDat$filling
    cur_val = cur_stimDat$meanPayoff

    annot = paste0("s: ", cur_shape, ", o: ", cur_orient, ", f: ", cur_filling, " \nvalue: ", cur_val)

    img = image_annotate(img, annot, size=80, gravity = "north")
  }


  return(grid::rasterGrob(img))
}


annotation_custom2 <- function (grob, xmin = -Inf, xmax = Inf, ymin = -Inf, ymax = Inf, data) {
  layer(data = data, stat = StatIdentity, position = PositionIdentity,
        geom = ggplot2:::GeomCustomAnn,
        inherit.aes = TRUE, params = list(grob = grob,
                                          xmin = xmin, xmax = xmax,
                                          ymin = ymin, ymax = ymax))
  }
