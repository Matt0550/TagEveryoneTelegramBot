import { publicApiGetAdminLogs } from '@/api/sdk.gen';
import type {
  PublicApiGetAdminLogsData,
  LogsResponse
} from '@/api/types.gen';
import { apiData } from '@/services/apiRuntime';

export const adminService = {
  getWeeklyLogs(query?: NonNullable<PublicApiGetAdminLogsData['query']>): Promise<LogsResponse> {
    return apiData<LogsResponse>(
      publicApiGetAdminLogs({ query })
    );
  }
};
