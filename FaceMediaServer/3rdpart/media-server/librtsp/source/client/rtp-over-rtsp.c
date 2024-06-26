#include "rtp-over-rtsp.h"
#include "rtp-header.h"
#include <stdlib.h>
#include <string.h>
#include <assert.h>

#define VMIN(x, y) ((x) < (y) ? (x) : (y))

enum rtp_over_tcp_state_t
{
	rtp_start = 0,
	rtp_channel,
	rtp_length_1,
	rtp_length_2,
	rtp_data,
};

static int rtp_alloc(struct rtp_over_rtsp_t *rtp)
{
	void* p;
	if (rtp->capacity < rtp->length)
	{
		p = realloc(rtp->data, rtp->length);
		if (!p)
			return -1;
		rtp->data = (uint8_t*)p;
		rtp->capacity = rtp->length;
	}
	return 0;
}

#if defined(RTP_OVER_RTSP_TRY_TO_FIND_NEXT_PACKET)
// skip missing data, find next start
static const uint8_t* rtp_over_rtsp_try_to_find_next_packet(struct rtp_over_rtsp_t* rtp, const uint8_t* data, const uint8_t* end)
{
	const uint8_t* p;
	p = (const uint8_t*)memchr(data, '$', end - data);
	if (!p)
		return end; // not found

	rtp->check = 1;
	return p;
}
#endif

// 10.12 Embedded (Interleaved) Binary Data
// Stream data such as RTP packets is encapsulated by an ASCII dollar sign(24 hexadecimal), 
// followed by a one-byte channel identifier,
// followed by the length of the encapsulated binary data as a binary two-byte integer in network byte order.
const uint8_t* rtp_over_rtsp(struct rtp_over_rtsp_t *rtp, const uint8_t* data, const uint8_t* end)
{
	int n;

	for (n = 0; data < end; data++)
	{
		switch (rtp->state)
		{
		case rtp_start:
			if (*data != '$') {
#if defined(RTP_OVER_RTSP_TRY_TO_FIND_NEXT_PACKET)
				return rtp_over_rtsp_try_to_find_next_packet(rtp, data, end);
#else
				return end;
#endif
			}
			rtp->bytes = 0;
			rtp->state = rtp_channel;
			break;

		case rtp_channel:
			// The channel identifier is defined in the Transport header with 
			// the interleaved parameter(Section 12.39).
			rtp->channel = *data;
			rtp->state = rtp_length_1;
			break;

		case rtp_length_1:
			rtp->length = *data << 8;
			rtp->state = rtp_length_2;
			break;

		case rtp_length_2:
			rtp->length |= *data;
			rtp->state = rtp_data;
			break;

		case rtp_data:
			if (0 == rtp->bytes && 0 != rtp_alloc(rtp))
				return end;
			n = (int)(end - data);
			n = VMIN(rtp->length - rtp->bytes, n);
			memcpy(rtp->data + rtp->bytes, data, n);
			rtp->bytes += (uint16_t)n;

#if defined(RTP_OVER_RTSP_TRY_TO_FIND_NEXT_PACKET)
			if (rtp->bytes >= 12)
			{
				uint32_t ssrc;
				ssrc = *(uint32_t*)(rtp->data + 8);

				if (rtp->check)
				{
					if (rtp->channel >= sizeof(rtp->ssrc) / sizeof(rtp->ssrc[0])
						|| ssrc != rtp->ssrc[rtp->channel]
						|| RTP_VERSION != (*rtp->data >> 6))
					{
						rtp->state = rtp_start;
						return rtp_over_rtsp_try_to_find_next_packet(rtp, data, end);
					}

					rtp->check = 0;
				}
				else if(rtp->channel < sizeof(rtp->ssrc) / sizeof(rtp->ssrc[0]) && 0 == rtp->ssrc[rtp->channel])
				{
					assert(RTP_VERSION == (*rtp->data >> 6));
					//assert(0 == rtp->ssrc[rtp->channel] || ssrc == rtp->ssrc[rtp->channel]);
					rtp->ssrc[rtp->channel] = ssrc;
				}
			}
#endif

			data += n;

			if (rtp->bytes == rtp->length)
			{
				rtp->state = rtp_start;
				if(rtp->onrtp)
					rtp->onrtp(rtp->param, rtp->channel, rtp->data, rtp->length);
				return data;
			}
			break;

		default:
			assert(0);
			return end;
		}
	}

	return data;
}
