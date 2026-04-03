export function useGetDriveStatus() {

  const getClosedStatus = (drive) => {
    if (drive.is_active) return null;

    // Parse the deadline ("Apr 03, 2026") natively
    const deadlineMoment = new Date(drive.deadline);

    // set to 11:59:59 PM (Local Time) on that deadline day
    deadlineMoment.setHours(23, 59, 59, 999);

    // parse the exact UTC updated_at moment into local time
    // converts "2026-04-03 20:18:28" to "2026-04-03T20:18:28Z"
    let safeUpdatedStr = drive.updated_at.replace(' ', 'T');
    if (!safeUpdatedStr.endsWith('Z')) safeUpdatedStr += 'Z';

    const updatedMoment = new Date(safeUpdatedStr);

    // Strict comparison
    if (updatedMoment <= deadlineMoment) {
      return "Closed Early";
    } else {
      return "Closed";
    }
  }

  return { getClosedStatus }
}
