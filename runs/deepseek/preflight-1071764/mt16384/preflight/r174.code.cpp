void FieldBase::AddRawValue(const FIT_FLOAT64 rawValue, const FIT_UINT8 fieldArrayIndex)
{
    switch ( GetType() )
    {
        case FIT_BASE_TYPE_BYTE:
        case FIT_BASE_TYPE_ENUM:
        case FIT_BASE_TYPE_SINT8:
        case FIT_BASE_TYPE_UINT8:
        case FIT_BASE_TYPE_UINT8Z:
        {
            const FIT_UINT8 value = (FIT_UINT8)FieldBase::Round(rawValue);
            const size_t required = (size_t)(fieldArrayIndex + 1);
            if (values.size() < required)
            {
                values.resize(required);
            }
            values[fieldArrayIndex] = (FIT_BYTE)value;
            break;
        }

        case FIT_BASE_TYPE_SINT16:
        case FIT_BASE_TYPE_UINT16:
        case FIT_BASE_TYPE_UINT16Z:
        {
            const FIT_UINT16 value = (FIT_UINT16)FieldBase::Round(rawValue);
            const size_t offset = (size_t)fieldArrayIndex * sizeof(FIT_UINT16);
            const size_t required = offset + sizeof(FIT_UINT16);
            if (values.size() < required)
            {
                values.resize(required);
            }
            memcpy(&values[offset], &value, sizeof(value));
            break;
        }

        case FIT_BASE_TYPE_SINT32:
        case FIT_BASE_TYPE_UINT32:
        case FIT_BASE_TYPE_UINT32Z:
        {
            const FIT_UINT32 value = (FIT_UINT32)FieldBase::Round(rawValue);
            const size_t offset = (size_t)fieldArrayIndex * sizeof(FIT_UINT32);
            const size_t required = offset + sizeof(FIT_UINT32);
            if (values.size() < required)
            {
                values.resize(required);
            }
            memcpy(&values[offset], &value, sizeof(value));
            break;
        }

        case FIT_BASE_TYPE_FLOAT32:
        {
            const FIT_FLOAT32 float32Value = (FIT_FLOAT32)FieldBase::Round(rawValue);
            FIT_UINT32 value;
            memcpy(&value, &float32Value, sizeof(FIT_FLOAT32));
            const size_t offset = (size_t)fieldArrayIndex * sizeof(FIT_UINT32);
            const size_t required = offset + sizeof(FIT_UINT32);
            if (values.size() < required)
            {
                values.resize(required);
            }
            memcpy(&values[offset], &value, sizeof(value));
            break;
        }

        case FIT_BASE_TYPE_FLOAT64:
        {
            if ((FIT_UINT8)values.size() < ((fieldArrayIndex + 1) * sizeof(FIT_FLOAT64)))
            {
                values.resize((fieldArrayIndex + 1) * sizeof(FIT_FLOAT64));
            }
            memcpy(&values[(size_t)fieldArrayIndex * sizeof(FIT_FLOAT64)], &rawValue, sizeof(FIT_FLOAT64));
            break;
        }

        case FIT_BASE_TYPE_SINT64:
        {
            const FIT_SINT64 value = (FIT_SINT64)rawValue;
            const size_t offset = (size_t)fieldArrayIndex * sizeof(FIT_SINT64);
            const size_t required = offset + sizeof(FIT_SINT64);
            if (values.size() < required)
            {
                values.resize(required);
            }
            memcpy(&values[offset], &value, sizeof(value));
            break;
        }

        case FIT_BASE_TYPE_UINT64:
        case FIT_BASE_TYPE_UINT64Z:
        {
            const FIT_UINT64 value = (FIT_UINT64)rawValue;
            const size_t offset = (size_t)fieldArrayIndex * sizeof(FIT_UINT64);
            const size_t required = offset + sizeof(FIT_UINT64);
            if (values.size() < required)
            {
                values.resize(required);
            }
            memcpy(&values[offset], &value, sizeof(value));
            break;
        }

        default:
            break;
    }
}
