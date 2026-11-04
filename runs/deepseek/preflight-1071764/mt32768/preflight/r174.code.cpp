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
            const FIT_FLOAT64 roundedValue = FieldBase::Round(rawValue);
            const size_t needed = (size_t)(fieldArrayIndex + 1) * sizeof(FIT_UINT8);
            if ((FIT_UINT8)values.size() < needed)
            {
                values.resize(needed);
            }
            values[fieldArrayIndex] = (FIT_UINT8)roundedValue;
            break;
        }

        case FIT_BASE_TYPE_SINT16:
        case FIT_BASE_TYPE_UINT16:
        case FIT_BASE_TYPE_UINT16Z:
        {
            const FIT_FLOAT64 roundedValue = FieldBase::Round(rawValue);
            const FIT_UINT16 value = (FIT_UINT16)roundedValue;
            const size_t needed = (size_t)(fieldArrayIndex + 1) * sizeof(FIT_UINT16);
            if ((FIT_UINT8)values.size() < needed)
            {
                values.resize(needed);
            }
            memcpy(&values[(size_t)fieldArrayIndex * sizeof(FIT_UINT16)], &value, sizeof(value));
            break;
        }

        case FIT_BASE_TYPE_SINT32:
        case FIT_BASE_TYPE_UINT32:
        case FIT_BASE_TYPE_UINT32Z:
        {
            const FIT_FLOAT64 roundedValue = FieldBase::Round(rawValue);
            const FIT_UINT32 value = (FIT_UINT32)roundedValue;
            const size_t needed = (size_t)(fieldArrayIndex + 1) * sizeof(FIT_UINT32);
            if ((FIT_UINT8)values.size() < needed)
            {
                values.resize(needed);
            }
            memcpy(&values[(size_t)fieldArrayIndex * sizeof(FIT_UINT32)], &value, sizeof(value));
            break;
        }

        case FIT_BASE_TYPE_FLOAT32:
        {
            const FIT_FLOAT64 roundedValue = FieldBase::Round(rawValue);
            const FIT_FLOAT32 value = (FIT_FLOAT32)roundedValue;
            const size_t needed = (size_t)(fieldArrayIndex + 1) * sizeof(FIT_FLOAT32);
            if ((FIT_UINT8)values.size() < needed)
            {
                values.resize(needed);
            }
            memcpy(&values[(size_t)fieldArrayIndex * sizeof(FIT_FLOAT32)], &value, sizeof(value));
            break;
        }

        case FIT_BASE_TYPE_FLOAT64:
        {
            const size_t needed = (size_t)(fieldArrayIndex + 1) * sizeof(FIT_FLOAT64);
            if ((FIT_UINT8)values.size() < needed)
            {
                values.resize(needed);
            }
            memcpy(&values[(size_t)fieldArrayIndex * sizeof(FIT_FLOAT64)], &rawValue, sizeof(rawValue));
            break;
        }

        case FIT_BASE_TYPE_SINT64:
        {
            const FIT_SINT64 value = (FIT_SINT64)rawValue;
            const size_t needed = (size_t)(fieldArrayIndex + 1) * sizeof(FIT_SINT64);
            if ((FIT_UINT8)values.size() < needed)
            {
                values.resize(needed);
            }
            memcpy(&values[(size_t)fieldArrayIndex * sizeof(FIT_SINT64)], &value, sizeof(value));
            break;
        }

        case FIT_BASE_TYPE_UINT64:
        case FIT_BASE_TYPE_UINT64Z:
        {
            const FIT_UINT64 value = (FIT_UINT64)rawValue;
            const size_t needed = (size_t)(fieldArrayIndex + 1) * sizeof(FIT_UINT64);
            if ((FIT_UINT8)values.size() < needed)
            {
                values.resize(needed);
            }
            memcpy(&values[(size_t)fieldArrayIndex * sizeof(FIT_UINT64)], &value, sizeof(value));
            break;
        }

        default:
            break;
    }
}
