"""Explicit source-derived admission rules; frozen vendor schemas remain untouched.

This is offline request validation only. No vendor handler, URL fetching, image
inference or automatic chunking is supplied by this module.
"""
import base64
import binascii
import re
import struct
import zlib
from .core import ValidationError, UnsupportedCapability

OUTFIT_IDS = {'public:POST:/transfer-outfit-v2', 'mcp:transfer_outfit'}
OUTFIT_SOURCES = [
    {'source':'shipped-lua','path':'extension-extracted/PixelLab/generate-transfer-outfit-pro.lua',
     'sha256':'3165c4da551710485ae2bf4a4b644acbc8e370adbe20e23a650808729e983ac0','lines':[53,66],
     'scope':'largest input dimension; >256 unsupported, >80:3, >64:8, otherwise15'},
    {'source':'public-v2-description','pointer':'#/paths/~1transfer-outfit-v2/post/description',
     'scope':'output image_size32..256; max frames15/8/3 by output longest side'},
    {'source':'captured-mcp-description','id':'mcp:transfer_outfit',
     'scope':'32..64:15,65..80:8,81..256:3; split calls with same reference/seed'},
]


class RequestAdmissionError(ValidationError):
    def __init__(self, message, *, layer, rule=None):
        super().__init__(message)
        self.layer, self.rule = layer, rule

    def to_dict(self):
        return {**super().to_dict(), 'validation_layer':self.layer, 'rule':self.rule}


def outfit_frame_limit(longest_side):
    if type(longest_side) is not int or not 32 <= longest_side <= 256:
        raise RequestAdmissionError('Outfit output sides must be32..256',
                                    layer='source-derived',rule='outfit-output-size')
    return 15 if longest_side <= 64 else 8 if longest_side <= 80 else 3


def validate_source_semantics(ident, request):
    """Called AFTER frozen-schema validation. Never mutate/default request JSON."""
    if ident=='public:POST:/reduce-colors':
        return validate_reduce_colors_dimensions(request)
    if ident not in OUTFIT_IDS:
        return {'status':'not-covered','rules':[], 'unresolved':[]}
    def reject(message,rule):
        raise RequestAdmissionError(message,layer='source-derived',rule=rule)
    unresolved=[]
    if ident.startswith('public:'):
        count=len(request['frames'])
        longest=max(request['image_size'].values())
    else:
        frames=[request.get(k) for k in ('frames_base64','frame_urls')]
        if sum(v is not None for v in frames)!=1:
            reject('Supply exactly one of frames_base64 or frame_urls','outfit-frame-source')
        refs=[request.get(k) for k in ('reference_image_base64','reference_image_url')]
        if sum(v is not None for v in refs)!=1 or not next(v for v in refs if v is not None):
            reject('Supply exactly one nonempty outfit reference','outfit-reference-source')
        count=len(next(v for v in frames if v is not None))
        dimensions=[request.get('width'),request.get('height')]
        longest=max(v for v in dimensions if v is not None) if any(v is not None for v in dimensions) else None
        if any(v is None for v in dimensions):
            unresolved.append('Effective output dimensions require image metadata; URL/base64 inputs are not fetched or decoded by this validator')
    if count < 2:reject('Outfit transfer requires at least2frames','outfit-min-frames')
    cap=outfit_frame_limit(longest) if longest is not None else 15
    if count > cap:
        reject(f'Outfit transfer permits at most{cap}frames for the declared output size; split calls with the same reference and seed', 'outfit-size-frame-limit')
    return {'status':'incomplete' if unresolved else 'passed','rules':['outfit-min-frames','outfit-size-frame-limit'],
            'frame_count':count,'max_frames':cap if not unresolved else None,
            'max_frames_from_known_dimensions':cap,'unresolved':unresolved,'sources':OUTFIT_SOURCES}


REDUCE_SIZE_RECEIPT={
    'source':'observed-vendor-422',
    'path':'runtime/context-bw-2x2/000-response.json',
    'sha256':'0054ccf02bc84fbcecccc7ffaaa60c5acf8a7e4944ec74cc864f4f767ec7259d',
    'observed':'Image1=94x46, Image3=95x47; all images must share dimensions',
    'schema_pointer':'#/components/schemas/ReduceColorsRequest/properties/images/description',
}


def png_header_size(envelope):
    """Bounded PNG IHDR inspection only; no decompression, URL fetch or edits."""
    encoded=envelope['base64']
    if len(encoded)>44_739_248:
        raise RequestAdmissionError('Image envelope exceeds32MiB local encoded-image budget',layer='local-resource',rule='image-byte-budget')
    if encoded.startswith('data:'):
        if not encoded.startswith('data:image/png;base64,'):
            raise UnsupportedCapability('local.requests.png-header-size','Only PNG headers are inspected; no fallback decoder or image download')
        encoded=encoded.split(',',1)[1]
    if len(encoded)<44 or len(encoded)%4 or not re.fullmatch(r'[A-Za-z0-9+/]*={0,2}',encoded):
        raise RequestAdmissionError('Invalid base64 PNG envelope',layer='source-derived',rule='reduce-colors-png-header')
    try:header=base64.b64decode(encoded[:44],validate=True)
    except (ValueError,binascii.Error) as exc:
        raise RequestAdmissionError('Invalid base64 PNG header',layer='source-derived',rule='reduce-colors-png-header') from exc
    if len(header)!=33 or header[:16]!=b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR':
        raise UnsupportedCapability('local.requests.png-header-size','A valid PNG IHDR is required for offline dimension admission')
    if (zlib.crc32(header[12:29])&0xffffffff)!=struct.unpack('>I',header[29:33])[0]:
        raise RequestAdmissionError('Invalid PNG IHDR checksum',layer='source-derived',rule='reduce-colors-png-header')
    width,height=struct.unpack('>II',header[16:24])
    if not 1<=width<=8192 or not 1<=height<=8192 or width*height>16_777_216:
        raise RequestAdmissionError('PNG dimensions exceed local16,777,216pixel/8192side admission budget',layer='local-resource',rule='image-pixel-budget')
    return [width,height]


def validate_reduce_colors_dimensions(request):
    images=request['images']
    if len(images)>256 or sum(len(i['base64']) for i in images)>67_108_864:
        raise RequestAdmissionError('Shared-palette inspection exceeds256image/64MiB envelope budget',layer='local-resource',rule='shared-palette-inspection-budget')
    sizes=[png_header_size(i) for i in images]
    if any(size!=sizes[0] for size in sizes[1:]):
        raise RequestAdmissionError('All reduce-colors images must be the same size to share a palette',layer='source-derived',rule='reduce-colors-equal-dimensions')
    return {'status':'passed','rules':['reduce-colors-equal-dimensions'],'image_count':len(images),'image_size':sizes[0],
            'sources':[REDUCE_SIZE_RECEIPT],'unresolved':[],
            'inspection':'PNG signature/IHDR/CRC only; compressed pixels not decoded or validated; original request unchanged'}
