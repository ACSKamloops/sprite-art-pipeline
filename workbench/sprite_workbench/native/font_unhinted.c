/* Bounded FreeType process adapter; protocol is little-endian uint32/int32.
 * No font modifications, glyph-specific rules, or external input paths beyond
 * the caller's private byte snapshot and codepoint list. */
#include <ft2build.h>
#include FT_FREETYPE_H
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/resource.h>

#define PIXELS 16777216u
static void word(uint32_t v) {
    for (int i=0;i<4;i++) fputc((int)((v>>(8*i))&255u),stdout);
}
int main(int argc,char **argv) {
    if(argc!=5) return 2;
    struct rlimit mem={512u*1024u*1024u,512u*1024u*1024u};
    struct rlimit cpu={10,10};
    if(setrlimit(RLIMIT_AS,&mem)||setrlimit(RLIMIT_CPU,&cpu)) return 9;
    int size=atoi(argv[2]), count=atoi(argv[4]);
    if(size<1||size>512||count<1||count>4096) return 2;
    FILE *input=fopen(argv[3],"r"); if(!input) return 2;
    FT_Library lib; FT_Face face;
    if(FT_Init_FreeType(&lib)) return 3;
    if(FT_New_Face(lib,argv[1],0,&face)) {FT_Done_FreeType(lib);return 3;}
    if(FT_Set_Pixel_Sizes(face,0,(FT_UInt)size)) return 3;
    int major,minor,patch; FT_Library_Version(lib,&major,&minor,&patch);
    const FT_Int32 flags=FT_LOAD_RENDER|FT_LOAD_NO_HINTING|FT_LOAD_NO_AUTOHINT;
    fputs("SWFT1\n",stdout);word((uint32_t)major);word((uint32_t)minor);word((uint32_t)patch);word((uint32_t)flags);word((uint32_t)count);
    size_t pixels=0;
    for(int i=0;i<count;i++) {
        unsigned long cp;
        if(fscanf(input,"%lu",&cp)!=1||cp>0x10ffffu) return 2;
        /* Measure the unhinted outline before allocating its raster. */
        if(FT_Load_Char(face,cp,FT_LOAD_NO_HINTING|FT_LOAD_NO_AUTOHINT)) return 4;
        FT_Glyph_Metrics metrics=face->glyph->metrics;
        if(metrics.width<0||metrics.height<0||metrics.width/64>4096||metrics.height/64>4096) return 6;
        if(FT_Load_Char(face,cp,flags)) return 4;
        FT_GlyphSlot slot=face->glyph; FT_Bitmap *b=&slot->bitmap;
        if(b->pixel_mode!=FT_PIXEL_MODE_GRAY&&b->pixel_mode!=FT_PIXEL_MODE_MONO) return 5;
        size_t w=(b->width&&b->rows)?b->width:1,h=(b->width&&b->rows)?b->rows:1;
        if(w>4096||h>4096||w*h>PIXELS-pixels) return 6;
        pixels+=w*h;
        word((uint32_t)cp);word((uint32_t)w);word((uint32_t)h);
        word((uint32_t)slot->bitmap_left);word((uint32_t)-slot->bitmap_top);word((uint32_t)slot->advance.x);
        if(!b->width||!b->rows) fputc(0,stdout);
        else for(unsigned y=0;y<b->rows;y++) {
            const unsigned char *row=b->pitch>=0?b->buffer+y*(size_t)b->pitch:b->buffer+(b->rows-y-1)*(size_t)(-b->pitch);
            for(unsigned x=0;x<b->width;x++)
                fputc(b->pixel_mode==FT_PIXEL_MODE_GRAY?row[x]:(row[x/8]&(0x80>>(x%8))?255:0),stdout);
        }
    }
    fclose(input); FT_Done_Face(face); FT_Done_FreeType(lib);
    return fflush(stdout)?8:0;
}
